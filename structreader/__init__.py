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

import logging; log = logging.getLogger()
import struct


class StructReader:
    """Reads a struct from a binary file or buffer, and returns
    a dict with named fields.

    structDef: a list of (format, name) pairs, where format is the
    format string used by `struct`, and name is the field name.
    """
    def __init__(self, *structDef):
        self.fields = {}
        self.orderedFields = []

        fieldSize = {}
        offset = 0
        for field in structDef:
            typ, name = field
            if type(typ) is str:
                size = struct.calcsize(typ)
            else:
                size = struct.calcsize(typ.fmt)
            fieldSize[name] = size

            assert name not in self.fields, \
                "Duplicate field name '" + name + "'"

            field = {
                'name': name,
                'size': fieldSize[name],
                'offset': offset,
                'struct_fmt': typ,
            }
            self.fields[name] = field
            self.orderedFields.append(field)
            offset += size
        self._dataSize = offset

        def _unpack(buf, offset=0):
            """Unpack this struct from given buffer."""
            res = {}
            for field in structDef:
                typ, name = field
                if type(typ) is str:
                    data = struct.unpack_from(typ, buf, offset)
                    if len(data) == 1: data = data[0]
                else:
                    data = typ.read(file)
                res[name] = data
                offset += fieldSize[name]
            return res

        self._unpack = _unpack

    def _unpackFromFile(self, file):
        """Read this struct from given file."""
        return self._unpack(file.read(self._dataSize))


class BinaryObject:
    """Object which is instantiated by reading a struct from a file."""

    def readFromFile(self, file, offset=None, reader=None):
        """Read this object from given file."""
        if offset is not None: file.seek(offset)
        self._file_offset = file.tell()
        if reader is None: reader = self._reader
        data = reader._unpackFromFile(file)
        return self._unpackFromData(data)

    def _unpackFromData(self, data):
        for k, v in data.items():
            setattr(self, k, v)
        self.validate()
        return self


    def validate(self):
        """Perform whatever sanity checks on this object
        after reading it.
        """
        return True


def readString(file, maxlen=None, encoding='shift-jis'):
    """Read null-terminated string from file."""
    s = []
    while maxlen == None or len(s) < maxlen:
        b = file.read(1)
        if b == b'\0': break
        else: s.append(b)
    s = b''.join(s)
    if encoding is not None: s = s.decode()
    return s


def readStringWithLength(file, fmt, offset=None, encoding='shift-jis'):
    """Read a string, prefixed with its length.

    fmt: The struct format of the length.
    """
    if offset is not None: file.seek(offset)
    log.debug("string offset: 0x%X", offset)
    ln = file.read(fmt)
    log.debug("string length: 0x%x", ln)
    s  = file.read(ln)
    if encoding is not None:
        s = s.decode(encoding)
    return s
