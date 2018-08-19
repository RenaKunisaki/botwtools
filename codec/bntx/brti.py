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
#from .fresobject import FresObject
import tempfile
from codec.base.types import Offset, Offset64, StrOffs, Padding
from codec.base.strtab import StringTable
from structreader import StructReader, BinaryObject, readStringWithLength
from enum import Enum
from .pixelfmt import TextureFormat
from .pixelfmt.swizzle import Swizzle, BlockLinearSwizzle
from .png import PNG


class BRTI(BinaryObject):
    """A BRTI in a BNTX."""
    class ChannelType(Enum):
        Zero  = 0
        One   = 1
        Red   = 2
        Green = 3
        Blue  = 4
        Alpha = 5

    class TextureType(Enum):
        Image1D = 0
        Image2D = 1
        Image3D = 2
        Cube    = 3
        CubeFar = 8

    class TextureDataType(Enum):
        UNorm  = 1
        SNorm  = 2
        UInt   = 3
        SInt   = 4
        Single = 5
        SRGB   = 6
        UHalf  = 10

    defaultFileExt = 'png'
    _magic = b'BRTI'
    _reader = StructReader(
        ('4s',   'magic'),
        ('I',    'length'),
        ('Q',    'length2'),
        ('B',    'flags'),
        ('B',    'dimensions'),
        ('H',    'tile_mode'),
        ('H',    'swizzle_size'),
        ('H',    'mipmap_cnt'),
        ('H',    'multisample_cnt'),
        ('H',    'reserved1A'),
        ('B',    'fmt_dtype', lambda v: BRTI.TextureDataType(v)),
        ('B',    'fmt_type',  lambda v: TextureFormat.get(v)()),
        Padding(2),
        ('I',    'access_flags'),
        ('i',    'width'),
        ('i',    'height'),
        ('i',    'depth'),
        ('i',    'array_cnt'),
        ('i',    'block_height', lambda v: 2**v),
        ('H',    'unk38'),
        ('H',    'unk3A'),
        ('i',    'unk3C'),
        ('i',    'unk40'),
        ('i',    'unk44'),
        ('i',    'unk48'),
        ('i',    'unk4C'),
        ('i',    'data_len'),
        ('i',    'alignment'),
        ('4B',   'channel_types',lambda v:tuple(map(BRTI.ChannelType,v))),
        ('i',    'tex_type'),
        StrOffs( 'name'),
        Padding(4),
        Offset64('parent_offset'),
        Offset64('ptrs_offset'),
    )

    def _unpackFromData(self, data):
        super()._unpackFromData(data)
        self.name = readStringWithLength(self._file, '<H', self.name)
        self.dumpToDebugLog()

        self.swizzle = BlockLinearSwizzle(self.width,
            self.fmt_type.bytesPerPixel,
            self.block_height)
        #self.swizzle = Swizzle(self.width,
        #    self.fmt_type.bytesPerPixel,
        #    self.block_height)

        self._readMipmaps()
        self._readData()

        log.debug("Texture '%s' size %dx%dx%d, len=%d: %s", self.name,
            self.width, self.height, self.depth, self.data_len,
            ' '.join(map(lambda b: '%02X'%b, self.data[0:16])))

        return self


    def _readMipmaps(self):
        self.mipOffsets = []
        for i in range(self.mipmap_cnt):
            offs  = self.ptrs_offset + (i*8)
            entry = self._file.read('I', offs) #- base
            self.mipOffsets.append(entry)
        log.debug("mipmap offsets: %s",
            list(map(lambda o: '%08X' % o, self.mipOffsets)))


    def _readData(self):
        base = self._file.read('Q', self.ptrs_offset)
        log.debug("Data at 0x%X => 0x%X", self.ptrs_offset, base)
        self.data = self._file.read(self.data_len, base)


    def decode(self):
        self.pixels, self.depth = self.fmt_type.decode(self)
        return self.pixels


    def toData(self):
        self.decode()
        tempFile = tempfile.SpooledTemporaryFile()
        png = PNG(width=self.width, height=self.height,
            pixels=self.pixels, bpp=self.depth)
        png.writeToFile(tempFile)
        tempFile.seek(0)
        return tempFile.read()


    def validate(self):
        super().validate()
        return True
