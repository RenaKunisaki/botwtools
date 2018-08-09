import struct
aamp_data_type = {}


def read_aamp_type(file, typ):
    """Given type ID and file, read data of that type."""
    if typ not in aamp_data_type:
        raise TypeError("Unknown type: " + str(typ))

    return aamp_data_type[typ]['read'](file)

def get_type_name(typ):
    """Get type name by ID."""
    if typ not in aamp_data_type:
        raise TypeError("Unknown type: " + str(typ))

    return aamp_data_type[typ]['name']


def String(file):
    """Null-terminated string type."""
    res = []
    while True:
        b = file.read(1)
        if b == b'\0': break
        res.append(b)
    res = b''.join(res)
    try:
        res = res.decode('shift-jis')
    except LookupError:
        pass
    return res


def Bool(file):
    """Boolean type."""
    return file.read(4) != b'\0\0\0\0'


def VecF(n):
    """Float vector type with n elements."""
    fmt = '%df' % n
    size = struct.calcsize(fmt)
    def read(file):
        data = struct.unpack(fmt, file.read(size))
        return ', '.join(map(str, data))
    return read


def defType(id, fmt, name):
    """Define type.

    id:   Type ID.
    fmt:  `struct` format string, or reader function.
    name: Type name.
    """
    if type(fmt) is str:
        size = struct.calcsize(fmt)
        read = lambda f: struct.unpack(fmt, f.read(size))[0]
    elif callable(fmt):
        read = fmt
    else:
        raise TypeError(fmt)

    aamp_data_type[id] = {
        'name': name,
        'read': read,
    }

defType(0x00, Bool,   'bool')
defType(0x01, 'f',    'float')
defType(0x02, 'I',    'int')
defType(0x03, VecF(2),'Vec2f')
defType(0x04, VecF(3),'Vec3f')
# 0x05: unknown
defType(0x06, VecF(4),'Vec4f')
defType(0x07, String, 'string')
# 0x08: actor
defType(0x08, String, 'actor')
defType(0x14, String, 'string2')
