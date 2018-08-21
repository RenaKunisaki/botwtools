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
aamp_data_type = {}

def read_aamp_type(file, typ):
    """Given type ID and file, read data of that type."""
    if typ not in aamp_data_type:
        raise TypeError("Unknown type: 0x%X" % typ)

    return aamp_data_type[typ]['read'](file)

def get_type_name(typ):
    """Get type name by ID."""
    if typ not in aamp_data_type:
        raise TypeError("Unknown type: 0x%X" % typ)

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
    except LookupError: pass # decoder not available
    except UnicodeDecodeError:
        try: res = res.decode('utf-8')
        except UnicodeDecodeError: pass
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

#It's a Curve3
#2 uint32s + 30 floats per curve
#so sizeof(Curve) is 4*32 = 0x80
#sizeof(Curve2) = 0x100, then 0x180, then 0x200 for Curve4

def Curve(n):
    fmt = '%dI%df' % (n*2, n*30)
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

# eg: 0x01 = agl::util::Parameter<float>
defType(0x00, Bool,   'bool') # bool
defType(0x01, 'f',    'float') # float
defType(0x02, 'I',    'int') # int
defType(0x03, VecF(2),'Vec2f') # sead::Vector2<float>
defType(0x04, VecF(3),'Vec3f') # sead::Vector3<float>
defType(0x05, VecF(4),'Vec4f') # sead::Vector4<float>
defType(0x06, VecF(4),'color') # sead::Color4f
defType(0x07, String, 'string32') # sead::FixedSafeString<32>
defType(0x08, String, 'string64') # sead::FixedSafeString<64>
defType(0x09, Curve(1), 'curve1') # agl::utl::ParameterCurve<1u>
defType(0x0A, Curve(2), 'curve2') # agl::utl::ParameterCurve<2u>
defType(0x0B, Curve(3), 'curve3') # agl::utl::ParameterCurve<3u>
defType(0x0C, Curve(4), 'curve4') # agl::utl::ParameterCurve<4u>
# 0x0D: buffer_int - agl::utl::ParameterBuffer<int>
# 0x0E: buffer_float - agl::utl::ParameterBuffer<float>
defType(0x0F, String, 'string256') # sead::FixedSafeString<256>
# 0x10: quat - agl::utl::Parameter<sead::Quat<float>>
defType(0x11, 'I', 'uint') # uint
# 0x12: buffer_u32 - agl::utl::ParameterBuffer<unsigned int>
# 0x13: buffer_binary - agl::utl::ParameterBuffer<unsigned char>
defType(0x14, String, 'stringref') # sead::SafeStringBase<char>
# 0x15: none - agl::utl::Parameter<int *>, agl::utl::Parameter<float *>, agl::utl::Parameter<unsigned int *>, agl::utl::Parameter<unsigned char *>
