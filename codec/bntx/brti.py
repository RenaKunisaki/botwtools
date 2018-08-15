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
from codec.base.types import Offset, Offset64, StrOffs, Padding
from codec.base.strtab import StringTable
from structreader import StructReader, BinaryObject, readStringWithLength


class BRTI(BinaryObject):
    """A BRTI in a BNTX."""
    _magic = b'BRTI'
    _reader = StructReader(
        ('4s',   'magic'),
        ('I',    'length'),
        ('Q',    'length2'),
        ('B',    'flags'),
        ('B',    'dimensions'),
        ('H',    'tile_mode'),
        ('H',    'swizzle_size'),
        ('H',    'mimap_cnt'),
        ('H',    'multisample_cnt'),
        ('H',    'reserved1A'),
        ('I',    'format'),
        ('I',    'access_flags'),
        ('i',    'width'),
        ('i',    'height'),
        ('i',    'depth'),
        ('i',    'array_cnt'),
        ('i',    'block_height'), # log2
        ('H',    'unk38'),
        ('H',    'unk3A'),
        ('i',    'unk3C'),
        ('i',    'unk40'),
        ('i',    'unk44'),
        ('i',    'unk48'),
        ('i',    'unk4C'),
        ('i',    'data_len'),
        ('i',    'alignment'),
        ('4B',   'channel_types'),
        ('i',    'tex_type'),
        StrOffs( 'name'),
        Padding(4),
        Offset64(  'parent_offset'),
        #Padding(4),
        Offset64(  'ptrs_offset'),
    )

    def _unpackFromData(self, data):
        super()._unpackFromData(data)
        self.name = readStringWithLength(self._file, '<H', self.name)
        self.dumpToDebugLog()

        self.mipOffsets = []
        for i in range(self.mimap_cnt):
            offs  = self.ptrs_offset + (i*8)
            entry = self._file.read('I', offs) #- base
            self.mipOffsets.append(entry)
        log.debug("mipmap offsets: %s",
            list(map(lambda o: '%08X' % o, self.mipOffsets)))

        return self


    def validate(self):
        super().validate()
        return True
