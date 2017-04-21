#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       gui.py
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
import gobject as _gobject
import gio as _gio
import gtk as _gtk
import fileicon as _fileicon
import file_properties as _file_properties
import bookmarks

class Widget(_gtk.VBox):
	__gsignals__ = {'file-menu' : (_gobject.SIGNAL_RUN_LAST, _gobject.TYPE_BOOLEAN, (_gobject.TYPE_STRING, _gobject.TYPE_PYOBJECT,)),
					'current-directory-menu' : (_gobject.SIGNAL_RUN_LAST, _gobject.TYPE_BOOLEAN, (_gobject.TYPE_PYOBJECT,))}
	def __init__(self):
		_gtk.VBox.__init__(self)
		self.builder = _gtk.Builder()
		self.builder.add_from_file(_os.path.join(_os.environ["FILEMANAGER_PATH"], "widget.builder"))
		self.area = self.builder.get_object("Area")
		self.file_area = self.builder.get_object("FileArea")
		self.file_view = self.builder.get_object("FileView")
		self.file_view.connect("item-activated", self._item_activated)
		self.file_view.connect("button-press-event", self._handler_click)
		self.file_model = self.builder.get_object("FileModel")
		self.path_label = self.builder.get_object("Path")
		self.search_entry = self.builder.get_object("FileNameEntry")
		self.search_entry.connect("activate", self._searchentry_callback)
		self.search_entry.connect("icon-press", self._searchentry_callback)
		self.completion = _gtk.EntryCompletion()
		self.completion.set_model(self.file_model)
		self.search_entry.set_completion(self.completion)
		pixbufcell = _gtk.CellRendererPixbuf()
		self.completion.pack_start(pixbufcell)
		self.completion.add_attribute(pixbufcell, 'pixbuf', 0)
		self.completion.add_attribute(pixbufcell, 'icon-name', 1)
		self.completion.set_text_column(3)
		self.pack_start(self.area, True, True, 0)
		self.area.show_all()
		self.bookmarks = self.builder.get_object("Bookmarks")
		self.bookmarks.connect("row-activated", self.bookmark_item_activated)
		bookmarks_column = self.builder.get_object("BookmarksColumn")
		bookmarks_column.set_title(_("Bookmarks"))
		self.bookmarks_model = self.builder.get_object("BookmarksStore")
		self.bookmarks_manager = bookmarks.BookmarksManager()
		self.bookmarks_manager.connect("update-bookmarks", self.update_bookmarks)
		self.load_bookmarks()
		self.mounts = self.builder.get_object("Mounts")
		mounts_column = self.builder.get_object("MountsColumn")
		mounts_column.set_title(_("Mounts"))
		self.mounts.connect("row-activated", self.mount_item_activated)
		self.mounts_model = self.mounts.get_model()
		self.volume_monitor = _gio.volume_monitor_get()
		self.volume_monitor.connect("mount-added", self.mount_update)
		self.volume_monitor.connect("mount-changed", self.mount_update)
		self.volume_monitor.connect("mount-removed", self.mount_update)
		self.load_mounts()
	
	def mount_update(self, monitor, mount):
		self.load_mounts()
	
	def mount_item_activated(self, widget, iter, path):
		self.open_file(self.mounts_model[iter][-1])
	
	def load_mount(self, mount):
		root = mount.get_root()
		icon = mount.get_icon().get_names()
		index = 0
		pixbuf, icon_name = _fileicon.get_file_icon_from_name(root.get_path())
		self.mounts_model.append([icon_name, mount.get_name(), root.get_uri()])
	
	def load_mounts(self):
		self.mounts_model.clear()
		for mount in self.volume_monitor.get_mounts():
			self.load_mount(mount)
	
	def bookmark_item_activated(self, widget, iter, path):
		self.open_file(self.bookmarks_model[iter][-1])
	
	def update_bookmarks(self, manager):
		self.bookmarks_model.clear()
		self.load_bookmarks()
	
	def load_bookmarks(self):
		bookmarks = self.bookmarks_manager.get_bookmarks()
		for i in bookmarks:
			self.bookmarks_model.append(["inode-directory", i[0], i[1].get_uri()])
	
	def _handler_click(self, widget, event):
		button = event.button
		pos = (event.x, event.y)
		time = event.time
		path = widget.get_path_at_pos(int(pos[0]), int(pos[1]))
		if button == 3:
			menu = _gtk.Menu()
			if path != None:
				open = _gtk.MenuItem(_("Open"))
				open.connect("activate", self._open_activate, self.file_model[path][4])
				open.show()
				menu.append(open)
				separator = _gtk.SeparatorMenuItem()
				separator.show()
				menu.append(separator)
				if self.emit("file-menu", self.file_model[path][4], menu):
					separator = _gtk.SeparatorMenuItem()
					separator.show()
					menu.append(separator)
				properties = _gtk.MenuItem(_("Properties"))
				properties.connect("activate", self._display_file_properties, self.file_model[path][4])
				properties.show()
				menu.append(properties)
				menu.show_all()
				menu.popup(None, None, None, button, time)
			elif self.emit("current-directory-menu", menu):
					menu.show_all()
					menu.popup(None, None, None, button, time)
			
	
	def _display_file_properties(self, widget, uri):
		dialog = _file_properties.FilePropertiesDialog(uri)
		dialog.show()
	
	def _open_activate(self, widget, path):
		self.open_file(path)
	
	def go_up(self):
		up_directory = _gio.File(path=_os.path.join(_os.path.split(self.path[:-1])[:-1])[0])
		self.set_current_directory(up_directory.get_uri())
	
	def _searchentry_callback(self, widget, icon_pos=None, event=None):
		text = widget.get_text()
		if text:
			self.open_file(_gio.File(path=_os.path.join(self.path, text)).get_uri())
	
	def open_file(self, uri):
		gfile = _gio.File(uri=uri)
		path = gfile.get_path()
		if _os.path.isdir(path):
			self.set_current_directory(uri)
	
	def _item_activated(self, widget, path):
		self.open_file(self.file_model[path][4])
	
	def get_current_directory(self):
		return self.uri
	
	def _current_dir_changed(self, monitor, file, other_file, event_type):
		self.set_current_directory(self.uri)
					
	def set_current_directory(self, uri):
		self.file_model.clear()
		self.uri = uri
		gfile = _gio.File(uri=uri)
		self.path = gfile.get_path()
		if self.path[-1] != "/":
			self.path += "/"
		if self.uri[-1] != "/":
			self.uri += "/"
		if gfile.get_uri_scheme() != "file":
			self.path_label.set_text(uri)
		else:
			self.path_label.set_text(self.path)
		self.file_monitor = gfile.monitor_directory(flags=_gio.FILE_MONITOR_NONE, cancellable=None)
		self.file_monitor.connect("changed", self._current_dir_changed)
		self.search_entry.set_text("")
		for i in _os.listdir(self.path):
			if i[0] != ".":
				file = _os.path.join(self.path, i)
				pixbuf, icon_name = _fileicon.get_file_icon_from_name(file)
				len_i = len(i)
				if len_i > 17:
					list_i = [i.decode("utf-8")]
					while len(list_i[-1]) > 17:
						new = [list_i[-1][:16], list_i[-1][16:]]
						list_i = list_i[:-1] + new
					display_name = "\n".join(list_i).encode("utf-8")
				else:
					display_name = i
				self.file_model.append([pixbuf, icon_name, display_name, i, _os.path.join(self.uri, i)])
