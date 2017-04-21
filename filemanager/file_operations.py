#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       file_operations.py
#       
#       Copyright 2011 Daniel Francis <santiago.danielfrancis@gmail.com>, Ignacio Rodríguez <nachoel01@gmail.com>
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
import commands as _commands
import gtk as _gtk

def raise_error(msg):
	builder = _gtk.Builder()
	builder.add_from_file(_os.path.join(_os.environ["FILEMANAGER_PATH"], "error.builder"))
	dialog = builder.get_object("Dialog")
	dialog.set_property("text", _("There was an error"))
	dialog.format_secondary_text(str(msg))
	dialog.run()
	dialog.destroy()

def copy(src, dest):
	output = _commands.getstatusoutput(""" cp -R "%s" "%s" """ % (src, dest))
	if output[0] > 0:
		raise_error(output[1])
		
def delete(src):
	output = _commands.getstatusoutput("""rm -Rf "%s" """ % src)
	if output[0] > 0:
		raise_error(output[1])

def new_directory(path):
	builder = _gtk.Builder()
	builder.add_from_file(_os.path.join(_os.environ["FILEMANAGER_PATH"], "new_directory.builder"))
	dialog = builder.get_object("dialog")
	dialog.set_title(_("Directory Name"))
	dialog.show()
	response = dialog.run()
	if response:
		new_name = builder.get_object("entry").get_text()
		if not new_name:
			new_name = _("New Directory")
			exists = False
			if _os.path.exists(_os.path.join(path, new_name)):
				exists = True
				i = 1
				while exists:
					if _os.path.exists(_os.path.join(path, new_name + (" %d" % i))):
						i += 1
					else:
						exists = False
				new_name += " %d" % i
		output = _commands.getstatusoutput("""mkdir "%s" """ % _os.path.join(path, new_name))
		if output[0] > 0:
			raise_error(output[1])
	dialog.destroy()
