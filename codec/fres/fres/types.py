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

import struct
from structreader import readString, readStringWithLength

class BaseType:
    def __init__(self, name):
        self.name = name

    def read(self, buffer, offset):
        return struct.unpack_from(self.fmt, buffer, offset)


class Offset(BaseType):
    """An offset in an FRES file."""
    size = 4
    fmt  = 'I'


class Offset64(Offset):
    """A 64-bit offset in an FRES file."""
    size = 8
    fmt  = 'Q'


class StrOffs(Offset):
    """An offset to a string.

    If `length` is None, the string is null-terminated.
    If `length` is a number, the length is that many bytes.
    If `length` is a string, the length is an integer with that
        format before the actual string data.
    """

    def __init__(self, name, length='<H', encoding='shift-jis'):
        super().__init__(name)
        self.encoding = encoding
        self.lengthFmt = length

    # It would be nice to have a read() method which also goes and
    # fetches the actual string. But, that won't work if we're
    # reading from a buffer. Anyway, we might still want the offset.
    # Instead, we'll do this. This is called from
    # FresObject.readFromFRES().

    def readStr(self, file, offset):
        pos = file.tell()
        file.seek(offset)

        if self.lengthFmt is None: # null-terminated
            data = readString(file, encoding=None)
        elif type(self.lengthFmt) is int: # fixed length
            data = file.read(self.lengthFmt)
        else: # length-prefixed
            data = readStringWithLength(
                file, self.lengthFmt, encoding=None)

        if self.encoding is not None:
            data = data.decode(self.encoding)

        file.seek(pos)
        return data


class BaseType:
    def __init__(self, name):
        self.name = name

    def read(self, buffer, offset):
        return struct.unpack_from(self.fmt, buffer, offset)


class Padding(BaseType):
    """Some unused bytes that should always be zero."""
    def __init__(self, size=4):
        self.name = 'padding_%d' % id(self) # must be unique
        self.size = size
        self.fmt  = '%dB' % size

    def read(self, buffer, offset):
        for i in range(self.size):
            if buffer[i+offset] != 0:
                # probably we assumed something is padding, but it's not
                log.error("Padding byte at offset 0x%X is 0x%X",
                    i, buffer[i+offset])
        return None
