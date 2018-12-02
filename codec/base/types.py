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
from structreader import readString, readStringWithLength
from vmath import Vec3, Vec4, Matrix

SIZEOF_FLOAT  = 4
SIZEOF_DOUBLE = 8


# some type annotations
Path      = str
BinInput  = io.BufferedIOBase
BinOutput = io.BufferedIOBase
TxtOutput = io.TextIOBase
fopenMode = str


class BaseType:
    def __init__(self, name):
        self.name = name

    def read(self, buffer, offset):
        return struct.unpack_from(self.fmt, buffer, offset)


class Offset(BaseType):
    """An offset in an FRES file."""
    size = 4
    fmt  = 'I'

    def tostring(self, val):
        return '%10d (%08X)' % (val, val)


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

    def tostring(self, val):
        if type(val) is str: # we already replaced with actual string
            return '"%s"' % val
        else: # it's still the offset
            return super().tostring(val)


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


class Flags(BaseType):
    """A set of bitflags."""
    def __init__(self, name, flags, fmt='I'):
        self.name   = name
        self._flags = flags
        self.fmt    = fmt
        self.size   = struct.calcsize(fmt)

    def read(self, buffer, offset):
        val = struct.unpack_from(self.fmt, buffer, offset)[0]
        res = {'_raw':val}
        for name, mask in self._flags.items():
            res[name] = (val & mask) == mask
        return res


class Vec3f(BaseType):
    """A vector of 3 floats."""
    size = SIZEOF_FLOAT * 3
    def read(self, buffer, offset):
        x, y, z = struct.unpack_from('3f', buffer, offset)
        return Vec3(x, y, z)

class Vec3d(BaseType):
    """A vector of 3 doubles."""
    size = SIZEOF_DOUBLE * 3
    def read(self, buffer, offset):
        x, y, z = struct.unpack_from('3d', buffer, offset)
        return Vec3(x, y, z)

class Vec4f(BaseType):
    """A vector of 4 floats."""
    size = SIZEOF_FLOAT * 4
    def read(self, buffer, offset):
        x, y, z, w = struct.unpack_from('4f', buffer, offset)
        return Vec4(x, y, z, w)

class Vec4d(BaseType):
    """A vector of 4 doubles."""
    size = SIZEOF_DOUBLE * 4
    def read(self, buffer, offset):
        x, y, z, w = struct.unpack_from('4d', buffer, offset)
        return Vec4(x, y, z, w)

class Mat4x4f(BaseType):
    """A 4x4 matrix of floats."""
    size = SIZEOF_FLOAT * 4 * 4
    def read(self, buffer, offset):
        d = struct.unpack_from('16f', buffer, offset)
        return Matrix(
            d[ 0: 4],
            d[ 4: 8],
            d[ 8:12],
            d[12:16],
        )

class Mat4x4d(BaseType):
    """A 4x4 matrix of doubles."""
    size = SIZEOF_DOUBLE * 4 * 4
    def read(self, buffer, offset):
        d = struct.unpack_from('16d', buffer, offset)
        return Matrix(
            d[ 0: 4],
            d[ 4: 8],
            d[ 8:12],
            d[12:16],
        )

class Mat4x3f(BaseType):
    """A 4x3 matrix of floats."""
    size = SIZEOF_FLOAT * 4 * 3
    def read(self, buffer, offset):
        d = struct.unpack_from('12f', buffer, offset)
        return Matrix(
            d[ 0: 4],
            d[ 4: 8],
            d[ 8:12],
        )

class Mat4x3d(BaseType):
    """A 4x3 matrix of doubles."""
    size = SIZEOF_DOUBLE * 4 * 3
    def read(self, buffer, offset):
        d = struct.unpack_from('12d', buffer, offset)
        return Matrix(
            d[ 0: 4],
            d[ 4: 8],
            d[ 8:12],
        )

class Mat3x3f(BaseType):
    """A 3x3 matrix of floats."""
    size = SIZEOF_FLOAT * 3 * 3
    def read(self, buffer, offset):
        d = struct.unpack_from('9f', buffer, offset)
        return Matrix(
            d[0:3],
            d[3:6],
            d[6:9],
        )

class Mat3x3d(BaseType):
    """A 3x3 matrix of doubles."""
    size = SIZEOF_DOUBLE * 3 * 3
    def read(self, buffer, offset):
        d = struct.unpack_from('9d', buffer, offset)
        return Matrix(
            d[0:3],
            d[3:6],
            d[6:9],
        )
