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
from .fresobject import FresObject
from .types import Offset, Offset64, StrOffs, Padding
from structreader import StructReader, BinaryObject
from .fvtx import FVTX
from .lod import LODModel

class FSHP(FresObject):
    """A FSHP in an FMDL."""
    _magic = b'FSHP'
    _reader = StructReader(
        ('4s', 'magic'),
        ('I',  'unk04'),
        ('I',  'unk08'),
        ('I',  'unk0C'),

        StrOffs('name'),
        Padding(4),
        Offset64('fvtx_offset'), # => FVTX

        Offset64('lod_offset'), # => LOD models
        Offset64('fskl_idx_array_offs'), # => 00030002 00050004 00070006 00090008  000B000A 000D000C 000F000E 00110010

        Offset64('unk30'), # 0
        Offset64('unk38'), # 0

        # bounding box and bounding radius
        Offset64('bbox_offset'), # => about 24 floats, or 8 Vec3s, or 6 Vec4s
        Offset64('bradius_offset'), # => => 3F03ADA8 3EFC1658 00000000 00000D14  00000000 00000000 00000000 00000000

        Offset64('unk50'),
        ('I',  'flags'),
        ('H',  'index'),
        ('H',  'fmat_idx'),

        ('H',  'single_bind'),
        ('H',  'fvtx_idx'),
        ('H',  'skin_bone_idx_cnt'),
        ('B',  'vtx_skin_cnt'),
        ('B',  'lod_cnt'),
        ('I',  'vis_group_cnt'),
        ('H',  'fskl_array_cnt'),
        Padding(2),
        size = 0x70,
    )

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the FSHP from given FRES."""
        super().readFromFRES(fres, offset, reader)
        #log.debug("FSHP name='%s'", self.name)
        self.dumpToDebugLog()
        #self.dumpOffsets()

        self.fvtx = FVTX().readFromFRES(fres, self.fvtx_offset)
        self.lods = []
        for i in range(self.lod_cnt):
            model = LODModel().readFromFRES(fres,
                self.lod_offset + (i * LODModel._reader.size))
            model.readFaces(self.fvtx)
            self.lods.append(model)

        self.lods = [self.lods[0]] # XXX DEBUG only keep last model

        return self


    def validate(self):
        super().validate()
        return True
