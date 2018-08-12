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
from structreader import StructReader, BinaryObject
from .bone import Bone

class FSKL(BinaryObject):
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

        ('Q',  'bone_idx_group_offs'),
        ('Q',  'bone_array_offs'),
        ('Q',  'inverse_idx_offs'),
        ('Q',  'inverse_mtx_offs'),

        ('Q',  'unk30'),

        ('I',  'flags'),
        ('H',  'num_bones'),
        ('H',  'num_inverse_idxs'),
        ('H',  'num_extra'),
        ('H',  'unk42'),
        ('I',  'unk44'),
    )

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the skeleton from given FRES."""
        super().readFromFile(fres.file, offset, reader)
        self.fres = fres
        self.dumpToDebugLog()
        self.dumpOffsets()

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
        self.inverse_idxs = []
        fres.file.seek(self.inverse_idx_offs)
        for i in range(self.num_inverse_idxs):
            self.inverse_idxs.append(fres.file.read('h'))
        log.debug("Inverse idxs: %s", self.inverse_idxs)

        # read inverse mtx
        self.inverse_mtx = []
        fres.file.seek(self.inverse_mtx_offs)
        for i in range(4):
            self.inverse_mtx.append(fres.file.read('4f'))
        log.debug("Inverse mtx: %s", self.inverse_mtx)

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
