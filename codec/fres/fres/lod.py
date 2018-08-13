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
        ('I',  'submesh_array_offs'),
        Padding(4),
        Offset64('unk08'),
        Offset64('unk10'),
        Offset64('idx_buf_offs'),
        ('I',  'face_offs'),
        ('I',  'prim_fmt'),
        ('I',  'face_type'),
        ('I',  'face_cnt'),
        ('H',  'vis_grp'),
        ('H',  'submesh_cnt'),
    )

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the model from given FRES."""
        super().readFromFRES(fres, offset, reader)

        #self.dumpToDebugLog()

        self.data = []
        fres.file.seek(self.face_offs + fres.rlt.data_start)
        if self.face_type == 1:
            for i in range(self.face_cnt):
                self.data.append(fres.file.read('H'))

        return self


    def validate(self):
        super().validate()
        return True
