#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       clipboard.py
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

import gtk as _gtk

def get_file_uri():
	clipboard = _gtk.Clipboard()
	contents = clipboard.wait_for_contents("text/uri-list")
	if contents:
		return contents.data
	else:
		return None

def clipboard_get_func_cb(clipboard, selection_data, info, uri):
	selection_data.set('text/uri-list', 8, uri)

def clipboard_clear_func_cb(clipboard, uri):
	pass

def copy_file_to_clipboard(uri):
	clipboard = _gtk.Clipboard()
	clipboard.set_with_data([('text/uri-list', 0, 0)],
							clipboard_get_func_cb,
							clipboard_clear_func_cb,
							uri)
