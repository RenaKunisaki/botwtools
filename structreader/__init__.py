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


def escape(c):
    if type(c) is str: c = ord(c)
    if   c == 0x00: return '\\0'
    elif c == 0x08: return '\\t'
    elif c == 0x0A: return '\\n'
    elif c == 0x0D: return '\\r'
    elif c == 0x5C: return '\\\\'
    elif c <  0x20 or c > 0x7E: return '\\x%02X' % c
    else: return chr(c)


_fmts = {
    'c': escape,
    'b': lambda v: '%10d (      %02X)' % (v, v),
    'B': lambda v: '%10d (      %02X)' % (v, v),
    'h': lambda v: '%10d (    %04X)' % (v, v),
    'H': lambda v: '%10d (    %04X)' % (v, v),
    'i': lambda v: '%10d (%08X)' % (v, v),
    'I': lambda v: '%10d (%08X)' % (v, v),
    'l': lambda v: '%10d (%08X)' % (v, v),
    'L': lambda v: '%10d (%08X)' % (v, v),
    # these sould use %20d but I don't expect to see values that
    # large, and the extra space is ugly.
    # same goes for the shorter fields above.
    'q': lambda v: '%10d (%08X %08X)' % (v, v >> 32, v & 0xFFFFFFFF),
    'Q': lambda v: '%10d (%08X %08X)' % (v, v >> 32, v & 0xFFFFFFFF),
    'n': lambda v: '%10d (%08X %08X)' % (v, v >> 32, v & 0xFFFFFFFF),
    'N': lambda v: '%10d (%08X %08X)' % (v, v >> 32, v & 0xFFFFFFFF),
    'P': lambda v: '0x%X' % v,
    'f': lambda v: '%5.3f' % v,
    'd': lambda v: '%5.3f' % v,
}
_fmtNames = {
    '?': 'bool',
    'b': ' int8_t',
    'B': 'uint8_t',
    'c': 'char',
    'd': 'double',
    'f': 'float',
    'h': ' int16_t',
    'H': 'uint16_t',
    'i': ' int32_t',
    'I': 'uint32_t',
    'l': ' int32_t',
    'L': 'uint32_t',
    'n': 'ssize_t',
    'N': ' size_t',
    'P': 'void*',
    'q': ' int64_t',
    'Q': 'uint64_t',
    's': 'char',
}
def fmtStructField(fmt, val):
    if type(fmt) is not str:
        return fmt.name, val

    func = _fmts.get(fmt, str)
    cnt  = 0
    while fmt[0] in '0123456789':
        cnt = (cnt*10) + int(fmt[0])
        fmt = fmt[1:]
    name = _fmtNames.get(fmt, fmt)
    if cnt > 1: name = '%s[%d]' % (name, cnt)
    return name, func(val)


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
            if type(field) is tuple:
                typ, name = field
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
            res[field['name']] = data
            offset += field['size']
        return res


    def unpackFromFile(self, file):
        """Read this struct from given file."""
        return self.unpackFromData(file.read(self.size))


class BinaryObject:
    """Object which is instantiated by reading a struct from a file."""
    def __init__(self):
        self._file = None
        self._file_offset = None


    def readFromFile(self, file, offset=None, reader=None):
        """Read this object from given file."""
        if offset is not None: file.seek(offset)
        self._file = file
        self._file_offset = file.tell()
        #log.debug("Reading %s from 0x%08X",
        #    type(self).__name__, self._file_offset)
        if reader is None: reader = self._reader
        log.debug("Struct %s size is 0x%X", type(self).__name__,
            reader.size)
        data = reader.unpackFromFile(file)
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
        if hasattr(self, '_magic'):
            if not self._checkMagic():
                raise TypeError("%s invalid magic: %s" %
                    (type(self).__name__, self.magic))
        return True


    def _checkMagic(self):
        magic = self._magic
        if type(magic) not in (list, tuple):
            magic = (magic,)
        return self.magic in magic


    def dumpToDebugLog(self):
        """Dump to debug log."""
        cls = type(self).__name__
        log.debug("%s dump:", cls)
        for name, field in self._reader.fields.items():
            val = getattr(self, name)
            typ = field['type']
            tp, vs = fmtStructField(typ, val)
            log.debug("[%04X] %12s %28s: %10s",
                field['offset'], tp, name, vs)


    def dumpOffsets(self):
        """Dump the values found at each field treated as an offset."""
        for name, field in self._reader.fields.items():
            val = getattr(self, name)
            if type(val) is int and val > 0xF and val < 0xFFFFFF:
                try:
                    data = []
                    for i in range(8):
                        data.append(self._file.read('I', val + (i*4)))
                    data = ' '.join(map(lambda v: '%08X' % v, data))
                except struct.error:
                    data = "<out of range>"
                log.debug("%28s %06X => %s", name, val, data)


def readString(file, maxlen=None, encoding='shift-jis'):
    """Read null-terminated string from file."""
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
    s  = file.read(ln)
    if encoding is not None:
        s = s.decode(encoding)
    return s
