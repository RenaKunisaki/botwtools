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

class LODModel(FresObject):
    """A Level-of-Detail Model."""
    _reader = StructReader(
        ('I',    'submesh_array_offs'),
        Padding( 4),
        Offset64('unk08'),
        Offset64('unk10'),
        Offset64('idx_buf_offs'),
        Offset(  'face_offs'),
        ('I',    'prim_fmt'),
        ('I',    'face_type'),
        ('I',    'face_cnt'),
        ('H',    'visibility_group'),
        ('H',    'submesh_cnt'),
        size = 0x34,
    )

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the model from given FRES."""
        super().readFromFRES(fres, offset, reader)
        #self.dumpToDebugLog()

        if self.face_type == 1:
            self.data = fres.read('H',
                pos=self.face_offs, count=self.face_cnt, use_rlt=True)
        else:
            log.error("Unsupported face type %d", self.face_type)

        return self


    def validate(self):
        super().validate()
        return True
