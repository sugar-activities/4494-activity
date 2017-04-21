#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       file_properties.py
#       
#       Copyright 2011 Daniel Francis <santiago.danielfrancis@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import os as _os
import stat as _stat
import time as _time
import gio as _gio
import gtk as _gtk
import gnomevfs as _gnomevfs
import file_size as _file_size

class FilePropertiesDialog(_gtk.Builder):
	def show(self):
		self.dialog.show()
		self.dialog.run()
		self.dialog.destroy()
	
	def __init__(self, uri):
		_gtk.Builder.__init__(self)
		gfile = _gio.File(uri=uri)
		self.path = gfile.get_path()
		self.add_from_file(_os.path.join(_os.environ["FILEMANAGER_PATH"], "file-properties-dialog.builder"))
		self.dialog = self.get_object("FilePropertiesDialog")
		self.dialog.set_title(_("Properties"))
		self.get_object("name_label").set_text(_("Name: "))
		self.name_entry = self.get_object("name_entry")
		self.get_object("type_label").set_text(_("Type: "))
		self.type_info = self.get_object("type_info")
		self.get_object("size_label").set_text(_("Size: "))
		self.size_notebook = self.get_object("size_notebook")
		self.size_info = self.get_object("size_info")
		self.find_size = self.get_object("find_size")
		self.find_size.set_label(_("Calculate"))
		self.get_object("location_label").set_text(_("Location: "))
		self.location_info = self.get_object("location_info")
		self.get_object("accessed_label").set_text(_("Accessed: "))
		self.accessed_info = self.get_object("accessed_info")
		self.get_object("modified_label").set_text(_("Modified: "))
		self.modified_info = self.get_object("modified_info")
		self.get_object("permissions_label").set_text(_("Permissions: "))
		self.get_object("Read").set_title(_("Read"))
		self.get_object("Write").set_title(_("Write"))
		self.exec_column = self.get_object("Exec")
		self.exec_column.set_title(_("Execution"))
		self.permissions_model = self.get_object("PermissionsModel")
		self.read_renderer = self.get_object("read-renderer")
		self.write_renderer = self.get_object("write-renderer")
		self.exec_renderer = self.get_object("exec-renderer")
		self.name_entry.connect("activate", self.change_filename)
		self.name_entry.set_text(_os.path.basename(self.path))
		fileinfo = gfile.query_info("standard::content-type")
		mime_type = _gio.content_type_get_mime_type(fileinfo.get_content_type())
		description = _gnomevfs.mime_get_description(mime_type)
		if description:
			self.type_info.set_text("%s (%s)" % (description, mime_type))
		else:
			self.type_info.set_text("%s" % mime_type)
		if _os.path.isdir(self.path):
			self.exec_column.set_title(_("Access"))
			self.size_notebook.set_current_page(1)
			self.find_size.connect("clicked", self.find_dir_size, self.path)
		else:
			self.size_notebook.set_current_page(0)
			self.size_info.set_text(_file_size.get_file_size(self.path))
		if gfile.get_uri_scheme() != "file":
			self.location_info.set_text(uri)
		else:
			self.location_info.set_text(self.path)
		stat = _os.stat(self.path)
		self.accessed_info.set_text(_time.ctime(stat.st_atime))
		self.modified_info.set_text(_time.ctime(stat.st_mtime))
		permissions = oct(_stat.S_IMODE(stat.st_mode))[1:]
		owner = bin(int(permissions[0]))[2:]
		while len(owner) != 3:
			owner = "0"+owner
		self.permissions_model.append([_("Owner"), bool(int(owner[0])), bool(int(owner[1])), bool(int(owner[2]))])
		group = bin(int(permissions[1]))[2:]
		while len(group) != 3:
			group = "0"+group
		self.permissions_model.append([_("Group"), bool(int(group[0])), bool(int(group[1])), bool(int(group[2]))])
		others = bin(int(permissions[2]))[2:]
		while len(others) != 3:
			others = "0"+others
		self.permissions_model.append([_("Others"), bool(int(others[0])), bool(int(others[1])), bool(int(others[2]))])
		self.read_renderer.connect("toggled", self.permissions_toggled)
		self.write_renderer.connect("toggled", self.permissions_toggled)
		self.exec_renderer.connect("toggled", self.permissions_toggled)
		
	def change_filename(self, widget):
		new_name = widget.get_text()
		if (not new_name) or ("/" in new_name):
			widget.set_text(_os.path.basename(self.path))
			return
		dirname = _os.path.dirname(self.path)
		_os.rename(self.path, _os.path.join(dirname, new_name))
		self.path = _os.path.join(dirname, new_name)
	
	def permissions_toggled(self, widget, path):
		if widget == self.read_renderer:
			number = 1
		elif widget == self.write_renderer:
			number = 2
		elif widget == self.exec_renderer:
			number = 3
		self.permissions_model[path][number] = not self.permissions_model[path][number]
		permissions = []
		for i in range(0, 3):
			user = None
			if list(self.permissions_model[i])[1:] == [True, True, True]:
				user = "7"
			elif list(self.permissions_model[i])[1:] == [True, True, False]:
				user = "6"
			elif list(self.permissions_model[i])[1:] == [True, False, True]:
				user = "5"
			elif list(self.permissions_model[i])[1:] == [True, False, False]:
				user = "4"
			elif list(self.permissions_model[i])[1:] == [False, True, True]:
				user = "3"
			elif list(self.permissions_model[i])[1:] == [False, True, False]:
				user = "2"
			elif list(self.permissions_model[i])[1:] == [False, False, True]:
				user = "1"
			elif list(self.permissions_model[i])[1:] == [False, False, False]:
				user = "0"
			permissions.append(user)
		_os.system("chmod %s %s" % ("".join(permissions), self.path))
	
	def find_dir_size(self, widget, path):
		cursor = _gtk.gdk.Cursor(_gtk.gdk.WATCH)
		self.dialog.window.set_cursor(cursor)
		self.size_notebook.set_current_page(0)
		self.size_info.set_text(_file_size.get_dir_size(path))
		cursor = _gtk.gdk.Cursor(_gtk.gdk.ARROW)
		self.dialog.window.set_cursor(cursor)
