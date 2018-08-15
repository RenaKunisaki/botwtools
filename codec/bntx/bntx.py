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
from structreader import StructReader, BinaryObject
from .nx import NX
from .brti import BRTI


class BNTX(BinaryObject):
    """BNTX texture pack."""
    _magic = b'BNTX'
    _reader = StructReader(
        ('4s',   'magic'),
        Padding(4),
        ('I',    'data_len'),
        ('H',    'byte_order'), # FFFE or FEFF
        ('H',    'version'),
        StrOffs( 'name'),
        Padding(2),
        ('H',    'strings_offs'), # relative to start of BNTX
        Offset(  'reloc_offs'),
        ('I',    'file_size'),
        size = 0x20,
    )

    def _unpackFromData(self, data):
        super()._unpackFromData(data)

        self.strings = StringTable().readFromFile(
            self._file, self._file_offset + self.strings_offs)

        self.nx = NX().readFromFile(self._file,
            self._file_offset + self._reader.size)
        self.nx.dumpToDebugLog()

        self.textures = []
        for i in range(self.nx.num_textures):
            offs = self._file.read('Q',
                self.nx.info_ptrs_offset+(i*8))
            brti = BRTI().readFromFile(self._file, offs)
            log.debug("Tex %d = %s", i, brti)
            self.textures.append(brti)

        return self


    def validate(self):
        super().validate()
        return True
