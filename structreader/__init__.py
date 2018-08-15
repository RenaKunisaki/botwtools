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
import struct
from .binaryobject import BinaryObject


BaseTypes = {
    int:    'I',
    float:  'f',
}


class StructReader:
    """Reads a struct from a binary file or buffer, and returns
    a dict with named fields.

    structDef: a list of (format, name) pairs, where format is the
    format string used by `struct`, and name is the field name.
    """
    def __init__(self, *structDef, size=None):
        _checkSize = size
        self.fields = {}
        self.orderedFields = []
        offset = 0
        for field in structDef:
            conv = None
            if type(field) is tuple:
                typ, name = field[0], field[1]
                if len(field) > 2: conv = field[2]
            else:
                typ, name = field, field.name

            assert name not in self.fields, \
                "Duplicate field name '" + name + "'"

            if type(typ) is str:
                if typ in BaseTypes: typ = BaseTypes[typ]
                size = struct.calcsize(typ)
                func = self._makeReader(typ)
            else:
                size = typ.size
                func = typ.read

            field = {
                'name':   name,
                'size':   size,
                'offset': offset,
                'type':   typ,
                'read':   func,
                'conv':   conv,
            }
            self.fields[name] = field
            self.orderedFields.append(field)
            offset += size
        self.size = offset

        if _checkSize is not None:
            assert _checkSize == self.size, \
                "Struct size is 0x%X but should be 0x%X" % (
                    self.size, _checkSize)


    def _makeReader(self, typ):
        """Necessary because lolscope"""
        return lambda buf, offs: struct.unpack_from(typ, buf, offs)


    def unpackFromData(self, buf, offset=0):
        """Read this struct from given data buffer."""
        res = {}
        for field in self.orderedFields:
            func = field['read']
            data = func(buf, offset)
            if type(data) is tuple and len(data) == 1:
                data = data[0] # grumble
            if field['conv']: data = field['conv'](data)
            res[field['name']] = data
            offset += field['size']
        return res


    def unpackFromFile(self, file):
        """Read this struct from given file."""
        return self.unpackFromData(file.read(self.size))


def readString(file, offset=None, maxlen=None, encoding='shift-jis'):
    """Read null-terminated string from file."""
    if offset is not None: file.seek(offset)
    s = []
    while maxlen == None or len(s) < maxlen:
        b = file.read(1)
        if b == b'\0': break
        else: s.append(b)
    s = b''.join(s)
    if encoding is not None: s = s.decode(encoding)
    return s


def readStringWithLength(file, fmt, offset=None, encoding='shift-jis'):
    """Read a string, prefixed with its length.

    fmt: The struct format of the length.
    """
    if offset is not None: file.seek(offset)
    #log.debug("string offset: 0x%X", offset)
    ln = file.read(fmt)
    #log.debug("string length: 0x%x", ln)
    s  = file.read(ln+1) # +1 for null byte
    if encoding is not None:
        s = s.decode(encoding)
    return s
