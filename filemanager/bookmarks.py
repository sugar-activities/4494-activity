#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       bookmarks.py
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

class BookmarksManager(_gobject.GObject):
	__gsignals__ = {'update-bookmarks' : (_gobject.SIGNAL_RUN_LAST, _gobject.TYPE_NONE, ())}
	def get_bookmarks(self):
		bookmarks_file = open(_os.path.join(_os.path.expanduser("~"), ".gtk-bookmarks"), "r")
		bookmarks = bookmarks_file.readlines()
		bookmarks_file.close()
		loaded_bookmarks = []
		loaded_bookmarks.append([_("Personal Directory"), _gio.File(path=_os.path.expanduser("~"))])
		loaded_bookmarks.append([_("File System"), _gio.File(path="/")])
		for i in bookmarks:
			all = i.split()
			gfile = _gio.File(all[0])
			if gfile.get_path():
				name = _os.path.basename(gfile.get_path())
				if len(all) == 2:
					name = all[-1]
				loaded_bookmarks.append([name, gfile])
		return loaded_bookmarks
	
	def __init__(self):
		_gobject.GObject.__init__(self)
		if not _os.path.exists(_os.path.join(_os.path.expanduser("~"), ".gtk-bookmarks")):
			open(_os.path.join(_os.path.expanduser("~"), ".gtk-bookmarks"), "w").close()
		gfile = _gio.File(_os.path.join(_os.path.expanduser("~"), ".gtk-bookmarks"))
		monitor = gfile.monitor_file(flags=_gio.FILE_MONITOR_NONE, cancellable=None)
		monitor.connect("changed", self._update_bookmarks)
	
	def _update_bookmarks(self, monitor, file, other_file, event_type):
		self.emit('update-bookmarks')
