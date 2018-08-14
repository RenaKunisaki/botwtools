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
from structreader import StructReader, BinaryObject

class Texture_NX(BinaryObject):
    """A 'NX' texture in a BNTX."""
    _magic = b'NX  '
    _reader = StructReader(
        ('4s',   'magic'),
        ('I',    'num_textures'),
        Offset64('info_ptrs_offset'),
        Offset64('data_blk_offset'),
        Offset64('dict_offset'),
        ('I',    'str_dict_len'),
    )

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the table from given FRES."""
        super().readFromFRES(fres, offset, reader)
        self.dumpToDebugLog()
        self.dumpOffsets()
        return self


class BNTX(BinaryObject):
    """A BNTX in a FRES."""
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

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the table from given FRES."""
        super().readFromFRES(fres, offset, reader)
        self.dumpToDebugLog()
        self.dumpOffsets()

        self.strings = self.fres.readStringTable(
            self._file_offset + self.strings_offs)

        self.nx = Texture_NX().readFromFRES(self.fres,
            self._file_offset + self._reader.size)

        return self


    def validate(self):
        super().validate()
        return True
