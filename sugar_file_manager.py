#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       sugar-file-manager
#       
#       Copyright 2011 Daniel Francis <santiago.danielfrancis@gmail.com>, Ignacio Rodríguez <nachoel01@gmail.com>.
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
import os
os.environ["FILEMANAGER_PATH"] = os.path.join(os.environ["SUGAR_BUNDLE_PATH"], "share", "sugar-file-manager")
import gettext
gettext.install("sugar-file-manager", os.path.join(os.path.dirname(__file__), "locale"))
import gio
import gtk
from sugar.activity import activity
from sugar.graphics.toolbutton import ToolButton
import filemanager

class SugarFileManagerActivity(activity.Activity):
	def mountjournal():
		name = _("Journal")
		if not os.path.exists(os.path.join(os.environ["HOME"], "%s" % name)):
			os.system("mkdir %s" % os.path.join(os.environ["HOME"], "%s" % name))
		if not os.path.ismount(os.path.join(os.environ["HOME"], "%s" % name)):
			command = "python ./mount_journal.py %s" % os.path.join(os.environ["HOME"], "%s" % name)
			print command
			print "*******************************************"
			os.system(command)
	mountjournal()
	
	def paste(self, widget, source, destination):
		filemanager.copy(gio.File(source).get_path(), gio.File(destination).get_path())
	
	def new_dir(self, widget, current_dir):
		filemanager.new_directory(gio.File(uri=current_dir).get_path())
	
	def current_directory_menu(self, widget, menu):
		create_directory = gtk.MenuItem(_("Create Directory"))
		create_directory.connect("activate", self.new_dir, widget.get_current_directory())
		create_directory.show()
		menu.append(create_directory)
		clipboard_data = filemanager.clipboard.get_file_uri()
		if clipboard_data:
			if clipboard_data + "/" != widget.get_current_directory() and os.path.dirname(clipboard_data) + "/" != widget.get_current_directory():
				_paste = gtk.MenuItem(_("Paste"))
				_paste.connect("activate", self.paste, clipboard_data, widget.get_current_directory())
				_paste.show()
				menu.append(_paste)
		return True
	
	def copy_file(self, widget, uri):
		filemanager.clipboard.copy_file_to_clipboard(uri)
	
	def delete_file(self, widget, uri):
		gfile = gio.File(uri=uri)
		filemanager.delete(gfile.get_path())
	
	def send_file_to(self, widget, src, dest):
		filemanager.copy(gio.File(src).get_path(), dest)
	
	def file_menu(self, widget, uri, menu):
		copy = gtk.MenuItem(_("Copy"))
		copy.connect("activate", self.copy_file, uri)
		copy.show()
		menu.append(copy)
		delete = gtk.MenuItem(_("Delete"))
		delete.connect("activate", self.delete_file, uri)
		delete.show()
		menu.append(delete)
		send_to = gtk.MenuItem(_("Send to"))
		send_to_menu = gtk.Menu()
		volume_monitor = gio.volume_monitor_get()
		for mount in volume_monitor.get_mounts():
			item = gtk.MenuItem(mount.get_name())
			item.show()
			item.connect("activate", self.send_file_to, uri, mount.get_root().get_path())
			send_to_menu.append(item)
		send_to.set_submenu(send_to_menu)
		send_to_menu.show()
		menu.append(send_to)
		send_to.show()
		return True
	
	def go_up_callback(self, widget, filemanager_widget):
		filemanager_widget.go_up()
	
	def refresh_callback(self, widget, filemanager_widget):
		filemanager_widget.set_current_directory(filemanager_widget.get_current_directory())
	
	def __init__(self, handle):
		activity.Activity.__init__(self, handle)
		self.toolbox = activity.ActivityToolbox(self)
		activity_toolbar = self.toolbox.get_activity_toolbar()
		activity_toolbar.share.props.visible = False
		activity_toolbar.keep.props.visible = False
		go_up = ToolButton("gtk-go-up")
		go_up.props.tooltip = _("Go Up")
		go_up.show()
		activity_toolbar.insert(go_up, 2)
		refresh = ToolButton("gtk-refresh")
		refresh.props.tooltip = _("Refresh")
		refresh.show()
		activity_toolbar.insert(refresh, 2)
		self.set_toolbox(self.toolbox)
		self.toolbox.show()
		widget = filemanager.Widget()
		go_up.connect("clicked", self.go_up_callback, widget)
		refresh.connect("clicked", self.refresh_callback, widget)
		widget.show()
		current_directory = gio.File(path=os.environ["HOME"])
		widget.set_current_directory(current_directory.get_uri())
		widget.connect("file-menu", self.file_menu)
		widget.connect('current-directory-menu', self.current_directory_menu)
		self.set_canvas(widget)
		self.show()
		
	def write_file(self, file_path):
		raise NotImplementedError
	
	def read_file(self, file_path):
		raise NotImplementedError
