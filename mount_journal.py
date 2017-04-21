#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Sascha Silbe <sascha-pgp@silbe.org> (PGP signed emails only)
# Modified by: Daniel Francis <santiago.danielfrancis@gmail.com> for usage in the Sugar File Manager
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""datastore-fuse: access the Sugar data store using FUSE

Mounting this "file system" allows "legacy" applications to access the Sugar
data store.
"""

import errno
import fuse
import logging
import operator
import os
import os.path
import shutil
import stat
import sys
import tempfile
import time

import dbus

from sugar.logger import trace
import sugar.logger
import sugar.mime


fuse.fuse_python_api = (0, 2)


DS_DBUS_SERVICE = "org.laptop.sugar.DataStore"
DS_DBUS_INTERFACE = "org.laptop.sugar.DataStore"
DS_DBUS_PATH = "/org/laptop/sugar/DataStore"

XATTR_CREATE = 1
XATTR_REPLACE = 2

# DBus still has no way to indicate an infinite timeout :-/
DBUS_TIMEOUT_MAX = 2**31 / 1000


class DataStoreObjectStat(fuse.Stat):

    # pylint: disable-msg=R0902,R0903
    def __init__(self, filesystem, metadata, size, inode):
        fuse.Stat.__init__(self, st_mode=stat.S_IFREG | 0750, st_ino=inode,
            st_uid=os.getuid(), st_gid=os.getgid(), st_size=size,
            st_mtime=self._parse_time(metadata.get('timestamp', '')))
        self.st_ctime = self.st_mtime
        self.st_atime = self.st_mtime
        tags = [tag for tag in metadata.get('tags', '').split()
            if tag and '/' not in tag]
        self.st_nlink = len(tags) + 1
        self.metadata = metadata
        self._filesystem = filesystem
        self.object_id = metadata['uid']

    def _parse_time(self, timestamp):
        try:
            return int(timestamp, 10)
        except ValueError:
            return 0

    def should_truncate(self):
        return self._filesystem.should_truncate(self.object_id)

    def reset_truncate(self):
        return self._filesystem.reset_truncate(self.object_id)


class Symlink(fuse.Stat):
    def __init__(self, filesystem, target, inode_nr):
        self._filesystem = filesystem
        self.target = target
        fuse.Stat.__init__(self, st_mode=stat.S_IFLNK | 0777, st_nlink=1,
            st_uid=os.getuid(), st_gid=os.getgid(), st_ino=inode_nr,
            st_mtime=time.time())
        self.st_ctime = self.st_mtime
        self.st_atime = self.st_mtime


class Directory(fuse.Stat):
    def __init__(self, path, parent_path, filesystem, mode):
        self._path = path
        self._filesystem = filesystem
        fuse.Stat.__init__(self, st_mode=stat.S_IFDIR | mode, st_nlink=2,
            st_uid=os.getuid(), st_gid=os.getgid(),
            st_mtime=time.time())
        self.st_ctime = self.st_mtime
        self.st_atime = self.st_mtime
        self.st_ino = filesystem.get_inode_number(path)

    def getxattr(self, name_, attribute_):
        # on Linux ENOATTR=ENODATA (Python errno doesn't contain ENOATTR)
        raise IOError(errno.ENODATA, os.strerror(errno.ENODATA))

    def listxattr(self, name_):
        return []

    def lookup(self, name_):
        raise IOError(errno.ENOENT, os.strerror(errno.ENOENT))

    def mkdir(self, name_):
        raise IOError(errno.EACCES, os.strerror(errno.EACCES))

    def mknod(self, name_):
        raise IOError(errno.EACCES, os.strerror(errno.EACCES))

    def readdir(self, offset_):
        yield fuse.Direntry('.',
            self._filesystem.get_inode_number(self._path))
        yield fuse.Direntry('..',
            self._filesystem.get_inode_number(self._parent_path))

    def readlink(self, name):
        entry = self.lookup(name)
        if not isinstance(entry, Symlink):
            raise IOError(errno.EINVAL, os.strerror(errno.EINVAL))

        return entry.target

    def remove(self, name_):
        raise IOError(errno.EACCES, os.strerror(errno.EACCES))

    def setxattr(self, name_, attribute_, value_, flags_):
        # On Linux ENOTSUP = EOPNOTSUPP
        raise IOError(errno.EOPNOTSUPP, os.strerror(errno.EOPNOTSUPP))


class ByTitleDirectory(Directory):
    def __init__(self, path, parent_path, filesystem):
        Directory.__init__(self, path, parent_path, filesystem, 0750)

    def readdir(self, offset):
        Directory.readdir(self, offset)

        for entry in self._find_entries():
            if 'uid' not in entry:
                # corrupted entry
                continue

            name = self._filesystem.lookup_title_name(entry['uid'])
            yield fuse.Direntry(name,
                ino=self._filesystem.get_inode_number(entry['uid']))

    @trace()
    def _find_entries(self):
        return self._filesystem.find({},
            {'metadata': ['title', 'uid', 'timestamp']})

    def getxattr(self, name, attribute):
        object_id = self._filesystem.resolve_title_name(name)
        metadata = self._filesystem.get_metadata(object_id)
        if attribute in metadata:
            return metadata[attribute]

        Directory.getxattr(self, object_id, attribute)

    def listxattr(self, name):
        object_id = self._filesystem.resolve_title_name(name)
        metadata = self._filesystem.get_metadata(object_id)
        return [str(name) for name in metadata.keys()]

    def lookup(self, name):
        object_id = self._filesystem.resolve_title_name(name)
        metadata = self._filesystem.get_metadata(object_id)
        size = self._filesystem.get_data_size(object_id)
        return DataStoreObjectStat(self._filesystem, metadata, size,
            self._filesystem.get_inode_number(object_id))

    def mknod(self, name):
        object_id = self._filesystem.create_new(name, '')

    def remove(self, name):
        object_id = self._filesystem.resolve_title_name(name)
        self._filesystem.remove_entry(object_id)

    def setxattr(self, name, attribute, value, flags):
        object_id = self._filesystem.resolve_title_name(name)
        metadata = self._filesystem.get_metadata(object_id)
        if flags & XATTR_CREATE and attribute in metadata:
            raise IOError(errno.EEXIST, os.strerror(errno.EEXIST))

        if flags & XATTR_REPLACE and attribute not in metadata:
            # on Linux ENOATTR=ENODATA (Python errno doesn't contain ENOATTR)
            raise IOError(errno.ENODATA, os.strerror(errno.ENODATA))

        metadata[attribute] = value
        self._filesystem.write_metadata(object_id, metadata)

class RootDirectory(ByTitleDirectory):
    def __init__(self, filesystem):
        ByTitleDirectory.__init__(self, '/', '/', filesystem)
        self.by_title_directory = self

    def readdir(self, offset_):
        for entry in ByTitleDirectory.readdir(self, offset_):
            yield entry

    def lookup(self, name):
        if name == 'by-id':
            return self.by_id_directory
        elif name == 'by-tags':
            return self.by_tags_directory

        return ByTitleDirectory.lookup(self, name)

    def remove(self, name):
        if name in ['by-id', 'by-tags']:
            raise IOError(errno.EACCES, os.strerror(errno.EACCES))

        return ByTitleDirectory.remove(self, name)


class DataStoreFile(object):

    _ACCESS_MASK = os.O_RDONLY | os.O_RDWR | os.O_WRONLY
    direct_io = False
    keep_cache = False

    @trace()
    def __init__(self, filesystem, path, flags, mode=None):
        self._filesystem = filesystem
        self._flags = flags
        self._read_only = False
        self._is_temporary = False
        self._dirty = False
        self._path = path

        # Contrary to what's documented in the wiki, we'll get passed O_CREAT
        # and mknod() won't get called automatically, so we'll have to take
        # care of all possible cases ourselves.
        if flags & os.O_EXCL:
            filesystem.mknod(path)
            entry = filesystem.getattr(path)
        else:
            try:
                entry = filesystem.getattr(path)

            except IOError, exception:
                if exception.errno != errno.ENOENT:
                    raise

                if not flags & os.O_CREAT:
                    raise

                filesystem.mknod(path, flags, mode)
                entry = filesystem.getattr(path)

        # mknod() might have created a symlink at our path...
        if isinstance(entry, Symlink):
            entry = filesystem.getattr(entry.target)

        self._object_id = entry.object_id
        self._read_only = flags & self._ACCESS_MASK == os.O_RDONLY

        if entry.should_truncate() or flags & os.O_TRUNC:
            self._file = self._create()
            entry.reset_truncate()
        else:
            self._file = self._checkout()

    def _create(self):
        self._is_temporary = True
        return tempfile.NamedTemporaryFile(prefix='datastore-fuse')

    def _checkout(self):
        name = self._filesystem.get_data(self._object_id)
        if not name:
            # existing, but empty entry
            return self._create()

        if self._read_only:
            return file(name)

        try:
            copy = self._create()
            shutil.copyfileobj(file(name), copy)
            copy.seek(0)
            return copy

        finally:
            os.remove(name)

    @trace()
    def read(self, length, offset):
        self._file.seek(offset)
        return self._file.read(length)

    @trace()
    def write(self, buf, offset):
        if self._flags & os.O_APPEND:
            self._file.seek(0, os.SEEK_END)
        else:
            self._file.seek(offset)

        self._file.write(buf)
        self._dirty = True
        return len(buf)

    @trace()
    def release(self, flags_):
        self.fsync()
        self._file.close()
        if not self._is_temporary:
            os.remove(self._file.name)

    @trace()
    def fsync(self, isfsyncfile_=None):
        self.flush()
        if self._read_only:
            return

        if self._dirty:
            self._filesystem.write_data(self._object_id, self._file.name)

    @trace()
    def flush(self):
        self._file.flush()

    @trace()
    def fgetattr(self):
        return self._filesystem.getattr(self._path)

    @trace()
    def ftruncate(self, length):
        self._file.truncate(length)

    def lock(self, cmd_, owner_, **kwargs_):
        raise IOError(errno.EACCES, os.strerror(errno.EACCES))


class DataStoreFS(fuse.Fuse):

    def __init__(self_fs, *args, **kw):
        # pylint: disable-msg=E0213
        class WrappedDataStoreFile(DataStoreFile):
            def __init__(self_file, *args, **kwargs):
                # pylint: disable-msg=E0213
                DataStoreFile.__init__(self_file, self_fs, *args, **kwargs)

        self_fs.file_class = WrappedDataStoreFile
        self_fs._truncate_object_ids = set()
        self_fs._object_id_to_title_name = {}
        self_fs._title_name_to_object_id = {}
        self_fs._max_inode_number = 1
        self_fs._object_id_to_inode_number = {}

        fuse.Fuse.__init__(self_fs, *args, **kw)

        bus = dbus.SessionBus()
        self_fs._data_store = dbus.Interface(bus.get_object(DS_DBUS_SERVICE,
            DS_DBUS_PATH), DS_DBUS_INTERFACE)
        self_fs._root = RootDirectory(self_fs)
        # TODO: listen to DS signals to update name mapping

    @trace()
    def getattr(self, path):
        components = [name for name in path.lstrip('/').split('/') if name]
        entry = self._root
        while components:
            entry = entry.lookup(components.pop(0))

        return entry

    @trace()
    def _delegate(self, path, action, *args):
        directory_name, file_name = os.path.split(path.strip('/'))
        directory = self.getattr(directory_name)
        return getattr(directory, action)(file_name, *args)

    def readdir(self, path, offset=None):
        return self.getattr(path).readdir(offset)

    def readlink(self, path):
        return self._delegate(path, 'readlink')

    def mknod(self, path, mode_=None, dev_=None):
        # called by FUSE for open(O_CREAT) before instantiating the file
        return self._delegate(path, 'mknod')

    def truncate(self, path, mode_=None, dev_=None):
        # Documented to be called by FUSE when opening files with O_TRUNC,
        # unless -o o_trunc_atomic is passed as a CLI option
        entry = self.getattr(path)
        if isinstance(entry, Directory):
            raise IOError(errno.EISDIR, os.strerror(errno.EISDIR))

        self._truncate_object_ids.add(entry.object_id)

    def unlink(self, path):
        self._delegate(path, 'remove')

    @trace()
    def utime(self, path_, times_):
        # TODO: update timestamp property
        return

    def mkdir(self, path, mode_):
        self._delegate(path, 'mkdir')

    @trace()
    def rmdir(self, path_):
        raise IOError(errno.EACCES, os.strerror(errno.EACCES))

    def rename(self, pathfrom, pathto):
        self._delegate(pathfrom, 'rename', pathto)

    @trace()
    def symlink(self, destination_, path_):
        # TODO for tags?
        raise IOError(errno.EACCES, os.strerror(errno.EACCES))

    @trace()
    def link(self, destination_, path_):
        raise IOError(errno.EACCES, os.strerror(errno.EACCES))

    @trace()
    def chmod(self, path_, mode_):
        raise IOError(errno.EACCES, os.strerror(errno.EACCES))

    @trace()
    def chown(self, path_, user_, group_):
        raise IOError(errno.EACCES, os.strerror(errno.EACCES))

    def getxattr(self, path, name, size):
        if not name.startswith('user.'):
            raise IOError(errno.ENODATA, os.strerror(errno.ENODATA))

        name = name[5:]
        value = self._delegate(path, 'getxattr', name)
        if not size:
            # We are asked for size of the value.
            return len(value)

        return str(value)

    def listxattr(self, path, size):
        attribute_names = ['user.' + name
            for name in self._delegate(path, 'listxattr')]
        if not size:
            # We are asked for the size of the \0-separated list.
            return reduce(operator.add,
                [len(name) + 1 for name in attribute_names], 0)

        return attribute_names

    def setxattr(self, path, name, value, flags):
        if not name.startswith('user.'):
            raise IOError(errno.EACCES, os.strerror(errno.EACCES))

        name = name[5:]
        return self._delegate(path, 'setxattr', name, value, flags)

    def should_truncate(self, object_id):
        return object_id in self._truncate_object_ids

    def reset_truncate(self, object_id):
        self._truncate_object_ids.discard(object_id)

    @trace()
    def find(self, metadata, options):
        mess = metadata.copy()
        mess.update(options)
        properties = mess.pop('metadata', [])
        logging.debug('mess=%r, properties=%r', mess, properties)
        return self._data_store.find(mess, properties,
            timeout=DBUS_TIMEOUT_MAX, byte_arrays=True)[0]

    def get_metadata(self, object_id):
        try:
            return self._data_store.get_properties(object_id,
                timeout=DBUS_TIMEOUT_MAX, byte_arrays=True)
        except Exception, exception:
            raise IOError(errno.ENOENT, str(exception))

    def create_new(self, name, path, tags=None):
        base_name = os.path.splitext(name)[0]
        metadata = {'title': base_name}
        mime_type = sugar.mime.get_from_file_name(name)
        if mime_type:
            metadata['mime_type'] = mime_type
        if tags:
            metadata['tags'] = ' '.join(tags)

        object_id = self._data_store.create(metadata, path, False,
            timeout=DBUS_TIMEOUT_MAX, byte_arrays=True)
        self._add_title_name(name, object_id)

    def remove_entry(self, object_id):
        try:
            self._data_store.delete(object_id)
        except Exception, exception:
            raise IOError(errno.ENOENT, str(exception))

        self._remove_title_name_by_object_id(object_id)
        self._truncate_object_ids.discard(object_id)

    def get_data(self, object_id):
        try:
            return self._data_store.get_filename(object_id,
                timeout=DBUS_TIMEOUT_MAX, byte_arrays=True)
        except Exception, exception:
            raise IOError(errno.ENOENT, str(exception))

    def get_data_size(self, object_id):
        try:
            file_name = self.get_data(object_id)
        except Exception, exception:
            raise IOError(errno.ENOENT, str(exception))

        if not file_name:
            return 0

        try:
            return os.stat(file_name).st_size
        finally:
            os.remove(file_name)

    @trace()
    def write_data(self, object_id, file_name):
        metadata = self.get_metadata(object_id)
        return self._data_store.update(object_id, metadata, file_name, False,
            timeout=DBUS_TIMEOUT_MAX, byte_arrays=True)

    def write_metadata(self, object_id, metadata):
        # Current data store doesn't support metadata-only updates
        file_name = self.get_data(object_id)
        return self._data_store.update(object_id, metadata, file_name,
            True, timeout=DBUS_TIMEOUT_MAX, byte_arrays=True)

    def resolve_title_name(self, name):
        if name not in self._title_name_to_object_id:
            # FIXME: Hack to fill self._title_name_to_object_id. To be
            # replaced by parsing the name and doing a specific search.
            list(self.readdir('/'))

        try:
            return self._title_name_to_object_id[name]

        except KeyError:
            raise IOError(errno.ENOENT, os.strerror(errno.ENOENT))

    def try_resolve_title_name(self, name):
        return self._title_name_to_object_id.get(name)

    def lookup_title_name(self, object_id):
        name = self._object_id_to_title_name.get(object_id)
        if name:
            return name

        metadata = self.get_metadata(object_id)
        name = self._generate_title_name(metadata, object_id)
        self._add_title_name(name, object_id)
        return name

    def _add_title_name(self, name, object_id):
        self._object_id_to_title_name[object_id] = name
        self._title_name_to_object_id[name] = object_id
        return name

    @trace()
    def _generate_title_name(self, metadata, object_id):
        title = metadata.get('title')
        name = title
        name = safe_name(name)
        extension = self._guess_extension(metadata.get('mime_type'), object_id)
        if extension:
            current_name = '%s.%s' % (name, extension)
        else:
            current_name = name
        counter = 1
        while current_name in self._title_name_to_object_id:
            counter += 1
            if extension:
                current_name = '%s %d.%s' % (name, counter, extension)
            else:
                current_name = '%s %d' % (name, counter)

        return current_name

    def _remove_title_name_by_object_id(self, object_id):
        name = self._object_id_to_title_name.pop(object_id, None)
        if name:
            del self._title_name_to_object_id[name]

    def _remove_title_name_by_name(self, name):
        object_id = self._title_name_to_object_id.pop(name, None)
        if object_id:
            del self._object_id_to_title_name[object_id]

    def get_inode_number(self, key):
        if key not in self._object_id_to_inode_number:
            inode_number = self._max_inode_number
            self._max_inode_number += 1
            self._object_id_to_inode_number[key] = inode_number

        return self._object_id_to_inode_number[key]

    def _guess_extension(self, mime_type, object_id):
        extension = None

        if not mime_type:
            file_name = self.get_data(object_id)
            if file_name:
                try:
                    mime_type = sugar.mime.get_for_file(file_name)
                finally:
                    os.remove(file_name)

        if mime_type:
            extension = sugar.mime.get_primary_extension(mime_type)

        return extension


def safe_name(name):
    return name.replace('/', '_')


def main():
    usage = "datastore-fuse: access the Sugar data store using FUSE\n"
    usage += fuse.Fuse.fusage

    # FIXME: figure out how to force options to on, properly.
    sys.argv += ['-o', 'use_ino']
    server = DataStoreFS(version="%prog " + fuse.__version__, usage=usage,
        dash_s_do='setsingle')
    server.parse(errex=1)
    sugar.logger.start()
    server.main()
    while True:
        pass

if __name__ == '__main__':
    main()
