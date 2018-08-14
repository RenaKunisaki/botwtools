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
from .fresobject import FresObject
from .types import Offset, Offset64, StrOffs, Padding
from structreader import StructReader, BinaryObject
from .bone import Bone

class FSKL(FresObject):
    """FSKL object header."""
    # offsets in this struct are relative to the beginning of
    # the FRES file.
    # I'm assuming they're 64-bit.
    _magic = b'FSKL'
    _reader = StructReader(
        ('4s', 'magic'),
        ('I',  'size'),
        ('I',  'size2'),
        ('I',  'unk0C'), # always 0

        Offset64('bone_idx_group_offs'),
        Offset64('bone_array_offs'),
        Offset64('inverse_idx_offs'),
        Offset64('inverse_mtx_offs'),

        Offset64('unk30'),

        ('I',  'flags'),
        ('H',  'num_bones'),
        ('H',  'num_inverse_idxs'),
        ('H',  'num_extra'),
        Padding(2),
        ('I',  'unk44'),
        size = 0x48,
    )

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the skeleton from given FRES."""
        super().readFromFRES(fres, offset, reader)
        #self.dumpToDebugLog()
        #self.dumpOffsets()
        log.info("Skeleton contains %d bones, %d inverse idxs, %d extras",
            self.num_bones, self.num_inverse_idxs, self.num_extra)

        # read bones
        self.bones = []
        self.bonesByName = {}
        offs = self.bone_array_offs
        for i in range(self.num_bones):
            b = Bone().readFromFRES(fres, offs)
            self.bones.append(b)
            if b.name in self.bonesByName:
                log.warn("Duplicate bone name '%s'", b.name)
                self.bonesByName[b.name] = b
            offs += Bone._reader.size

        # read inverse indices
        self.inverse_idxs = fres.read('h',
            pos   = self.inverse_idx_offs,
            count = self.num_inverse_idxs)
        #log.debug("Inverse idxs: %s", self.inverse_idxs)

        # read inverse mtx (which I assume is 4x4)
        self.inverse_mtx = fres.read('4f', count = 4,
            pos = self.inverse_mtx_offs)
        #log.debug("Inverse mtx: %s", self.inverse_mtx)

        return self


    def validate(self):
        #for field in self._reader.fields.values():
        #    val = getattr(self, field['name'])
        #    if type(val) is int:
        #        log.debug("FMDL[%04X] %16s = 0x%08X", field['offset'],
        #            field['name'], val)
        #    else:
        #        log.debug("FMDL[%04X] %16s = %s", field['offset'],
        #            field['name'], val)

        super().validate()
        return True
