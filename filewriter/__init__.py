# This file is part of botwtools.
#
# botwtools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# botwtools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with botwtools.  If not, see <https://www.gnu.org/licenses/>.

import logging; log = logging.getLogger(__name__)
import os
import io
import struct

Path = str # type declaration


def sanitizePath(path:Path):
    dirs = path.split('/')
    res  = []
    for i, d in enumerate(dirs):
        if d.startswith('.') and d != '.':
            d = 'data' + d
        #elif d == '':
        #    d = 'data'
        res.append(d)
    res = '/'.join(res)
    if res != path:
        log.warn("Changed path from %s to %s", path, res)
    return res


def mkdir(path:Path) -> Path:
    """Create a subdirectory within the output directory.

    Allows multiple nested paths (eg foo/bar/baz).
    Does nothing if the directory already exists.

    Returns the full, normalized path to the directory.
    """
    path = sanitizePath(path)
    if path != '':
        log.debug("mkdir path is '%s'", path)
        dirs = path.split('/')
        for i in range(len(dirs)):
            p = '/'.join(dirs[0:i+1])
            if p != '':
                log.debug("mkdir(%s)", p)
                try: os.mkdir(p)
                except FileExistsError: pass
    return path


class FileWriter:
    """Helper class for creating and writing
    binary files and directories.
    """
    _seekNames = {
        'start': 0,
        'cur':   1,
        'end':   2,
    }

    def __init__(self, file, mode='wb'):
        if type(file) is str:
            self._open(file, mode)
        else: self.file = file


    def _open(self, file, mode):
        path, name = os.path.split(sanitizePath(file))
        path = mkdir(path)
        if path == '': path = '.' # don't extract archives to /
        path += '/' + name
        if os.path.isdir(path):
            log.debug("FileWriter: path %s => %s", path,
                path+'/'+name)
            path += '/' + name
        self.file = open(path, mode)


    @staticmethod
    def open(path, mode='wb'):
        return FileWriter(file, mode)


    def seek(self, pos:int, whence:(int,str)=0) -> int:
        """Seek within the file.

        pos: Position to seek to.
        whence: Where to seek from:
            0 or 'start': Beginning of file.
            1 or 'cur':   Current position.
            2 or 'end':   Backward from end of file.

        Returns new position.
        """
        whence = self._seekNames.get(whence, whence)
        return self.file.seek(pos, whence)


    def write(self, data, fmt=None, pos:int=None) -> None:
        """Write to the file.

        data: Data to write.
        fmt:  struct format string to encode data.
        pos:  Position to seek to first. (optional)
        """
        if pos is not None: self.seek(pos)
        if fmt is not None: data = struct.pack(fmt, data)
        self.file.write(data)


    def tell(self) -> int:
        """Get current read position."""
        return self.file.tell()


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()

    def __str__(self):
        return "<FileWriter(%s) at 0x%x>" % (self.name, id(self))


class DummyFileWriter(FileWriter):
    """A FileWriter that discards all writes, for dry runs."""

    def _open(self, file, mode):
        # this should work even on Windows
        self.file = open(os.devnull, mode)
