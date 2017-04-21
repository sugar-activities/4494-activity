#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       fileicon.py
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

import gio as _gio
import gtk as _gtk

icon_theme = _gtk.icon_theme_get_default()
icons = icon_theme.list_icons()

def get_file_icon_from_name(name):
	gfile = _gio.File(name)
	fileinfo = gfile.query_info("standard::content-type")
	mime_type = _gio.content_type_get_mime_type(fileinfo.get_content_type())
	icon = _gio.content_type_get_icon(mime_type).get_names()
	index = 0
	icon_name = None
	pixbuf = None
	if "image-x-generic" in icon:
		try:
			pixbuf = _gtk.gdk.pixbuf_new_from_file_at_size(name, 64, 64)
		except:
			pixbuf = None
	if not pixbuf:
		while not (icon[index] in icons):
			index += 1
			if index >= len(icon):
				icon_name = "unknown"
				break
		if not icon_name:
			icon_name = icon[index]
	return pixbuf, icon_name
