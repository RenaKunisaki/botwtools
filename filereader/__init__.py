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
import io
import struct

class FileReader:
    """Helper class for reading binary files.

    Wraps a file object and provides additional methods and properties.
    """

    _seekNames = {
        'start': 0,
        'cur':   1,
        'end':   2,
    }

    def __init__(self, file, mode='rb'):
        if type(file) is str: file = open(file, mode)
        self.file = file
        self.name = file.name
        pos = file.tell()
        self.size = self.seek(0, 'end')
        file.seek(pos)


    @staticmethod
    def open(path, mode='rb'):
        file = open(path, mode)
        return FileReader(file)


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


    def read(self, size:(int,str)=-1, pos:int=None, count:int=1):
        """Read from the file.

        size:  Number of bytes to read, or a `struct` format string.
        pos:   Position to seek to first. (optional)
        count: Number of items to read. If not 1, returns a list.

        Returns the data read.
        """
        if pos is not None: self.seek(pos)
        if   count <  0: raise ValueError("Count cannot be negative")
        elif count == 0: return []

        res = []
        if type(size) is str:
            fmt  = size
            size = struct.calcsize(size)
            for i in range(count):
                r = struct.unpack(fmt, self.file.read(size))
                if len(r) == 1: r = r[0]
                res.append(r)
        else:
            for i in range(count):
                res.append(self.file.read(size))
        if count == 1: return res[0]
        return res


    def readString(self, pos:int=None, length:(int,str)=None,
    encoding:str='shift-jis') -> (str, bytes):
        """Read null-terminated string from file.

        pos: Position to seek to first. (optional)
        length: Length to read.
        encoding: What to decode the string as.
            If None, do not decode (return as bytes).

        If `length` is None, it reads a null-terminated string.
        If `length` is an integer, it reads that many bytes,
            even if there are embeded nulls.
        If `length` is a string, it specifies a `struct` format
            string; this value is read and used as the string length.

        Returns the string.
        """
        if pos is not None: self.seek(pos)
        pos = self.tell() # for error message
        s = []
        try:
            if type(length) is str: length = self.read(length)
            if length is None:
                while True:
                    b = self.file.read(1)
                    if b == b'\0': break
                    else: s.append(b)
                s = b''.join(s)
            else:
                s = self.file.read(length)
            if encoding is not None: s = s.decode(encoding)
        except (UnicodeDecodeError, struct.error):
            log.error("Can't decode string from 0x%X", pos)
            return None
        return s


    def tell(self) -> int:
        """Get current read position."""
        return self.file.tell()


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()

    def __str__(self):
        return "<FileReader(%s) at 0x%x>" % (self.name, id(self))
