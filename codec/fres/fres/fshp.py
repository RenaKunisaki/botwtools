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
from structreader import StructReader, BinaryObject, readStringWithLength
from .fvtx import FVTX
from .lod import LODModel

class FSHP(BinaryObject):
    """A FSHP in an FMDL."""
    _reader = StructReader(
        ('4s', 'magic'),  # 'FSHP'
        ('I',  'unk04'),
        ('I',  'unk08'),
        ('I',  'unk0C'),

        ('Q',  'name_offset'), # => string prefixed by u16 len
        ('Q',  'fvtx_offset'), # => FVTX

        ('Q',  'lod_offset'), # => 000018B0 00000000 0001E000 00000000  000018B8 00000000 00001900 00000000
        ('Q',  'fskl_idx_array_offs'), # => 00030002 00050004 00070006 00090008  000B000A 000D000C 000F000E 00110010

        ('Q',  'unk30'), # 0
        ('Q',  'unk38'), # 0

        # bounding box and bounding radius
        ('Q',  'bbox_offset'), # => about 24 floats, or 8 Vec3s, or 6 Vec4s
        ('Q',  'bradius_offset'), # => => 3F03ADA8 3EFC1658 00000000 00000D14  00000000 00000000 00000000 00000000

        ('Q',  'unk50'),
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
        ('H',  'padding6E'),
        # size: 0x70
    )

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the FSHP from given FRES."""
        super().readFromFile(fres.file, offset, reader)
        self.fres = fres
        self.name = readStringWithLength(fres.file,
            '<H', self.name_offset)
        log.debug("FSHP name='%s'", self.name)

        self.dumpToDebugLog()
        self.dumpOffsets()

        FVTX().readFromFRES(fres, self.fvtx_offset)
        self.lods = []
        for i in range(self.lod_cnt):
            self.lods.append(LODModel().readFromFRES(fres,
                self.lod_offset + (i * 56)))

        return self


    def validate(self):
        assert self.magic == b'FSHP', "Not an FSHP"
        return True
