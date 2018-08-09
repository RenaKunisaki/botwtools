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

import io
import struct

class FileReader:
    """Helper class for reading binary files."""
    _seekNames = {
        'start': 0,
        'cur':   1,
        'end':   2,
    }

    def __init__(self, file):
        self.file = file


    def seek(self, pos:int, whence:(int,str)=0):
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


    def read(self, size:(int,str)=-1, pos:int=None):
        """Read from the file.

        size: Number of bytes to read, or a `struct` format string.
        pos:  Position to seek to first. (optional)

        Returns the data read.
        """
        if pos is not None: self.seek(pos)
        if type(size) is str:
            return struct.unpack(size,
                self.file.read(struct.calcsize(size)))
        return self.file.read(size)


    def readString(self, pos:int=None, maxlen:int=None,
    encoding:str='shift-jis') -> (str, bytes):
        """Read null-terminated string from file.

        pos: Position to seek to first. (optional)
        maxlen: Maximum number of bytes to read. (optional)
        encoding: What to decode the string as.
            If None, do not decode (return as bytes).

        Returns the string.
        """
        if pos is not None: self.seek(pos)
        s = []
        while maxlen == None or len(s) < maxlen:
            b = self.file.read(1)
            if b == b'\0': break
            else: s.append(b)

        s = b''.join(s)
        if encoding is not None: s = s.decode()
        return s
