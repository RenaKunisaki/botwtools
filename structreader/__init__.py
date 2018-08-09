import logging; log = logging.getLogger()
import struct

class StructReader:
    """Reads a struct from a binary file or buffer, and returns
    a dict with named fields.

    structDef: a list of (format, name) pairs, where format is the
    format string used by `struct`, and name is the field name.
    """
    def __init__(self, *structDef):
        fmt = []
        fieldSize = {}
        for field in structDef:
            typ, name = field
            fmt.append(typ)
            fieldSize[name] = struct.calcsize(typ)
        fmt = ''.join(fmt)
        self._dataSize = struct.calcsize(fmt)

        def _unpack(buf, offset=0):
            """Unpack this struct from given buffer."""
            res = {}
            for field in structDef:
                typ, name = field
                data = struct.unpack_from(typ, buf, offset)
                res[name] = data[0]
                offset += fieldSize[name]
            return res

        self._unpack = _unpack

    def _unpackFromFile(self, file):
        """Read this struct from given file."""
        return self._unpack(file.read(self._dataSize))


class BinaryObject:
    """Object which is instantiated by reading a struct from a file."""

    def readFromFile(self, file):
        """Read this object from given file."""
        data = self._reader._unpackFromFile(file)
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
