#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       file_size.py
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
import gtk as _gtk

def get_file_size(path):
	orig = _os.path.getsize(path) 
	size = _os.path.getsize(path)
	pot = 0
	str_size = ""
	unit = ""
	while True:
		(size, other) = divmod(size, 1024)
		if not size:
			break
		pot += 1
		if pot == 4:
			break
		unit = "-KMGT"[pot]
		if not pot:
			str_size += "%d bytes" % orig
			break
	if not str_size:
		str_size += "%.1f %sb" % (orig/(1024.0**pot), unit)
	return str_size

def get_dir_size(path):
	total_size = 0
	for dirpath, dirnames, filenames in _os.walk(path): 
		for f in filenames: 
			fp = _os.path.join(dirpath, f)
			try:
				total_size += _os.stat(fp).st_size
			except:
				pass
	orig = total_size + 0
	pot = 0
	str_size = ""
	unit = ""
	while True:
		(total_size, other) = divmod(total_size, 1024)
		if not total_size:
			break
		pot += 1
		if pot == 4:
			break
		unit = "-KMGT"[pot]
		if not pot:
			str_size += "%d bytes" % orig
			break
	if not str_size:
		str_size += "%.1f%sB" % (orig/(1024.0**pot), unit)
	return str_size
