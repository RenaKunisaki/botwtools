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
import math
from .fresobject import FresObject
from codec.base.types import Offset, Offset64, StrOffs, Padding
from codec.base.dict  import Dict
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
        Padding(4),
        Offset64('bone_idx_group_offs'),
        Offset64('bone_array_offs'),
        Offset64('smooth_idx_offs'),
        Offset64('smooth_mtx_offs'),
        Offset64('unk30'),
        ('I',  'flags'),
        ('H',  'num_bones'),
        ('H',  'num_smooth_idxs'),
        ('H',  'num_rigid_idxs'),
        ('H',  'num_extra'),
        ('I',  'unk44'),
        size = 0x48,
    )

    FLAG_SCALE_NONE = 0x00000000 # no scaling
    FLAG_SCALE_STD  = 0x00000100 # standard scaling
    FLAG_SCALE_MAYA = 0x00000200 # Respects Maya's segment scale
        # compensation which offsets child bones rather than
        # scaling them with the parent.
    FLAG_SCALE_SOFTIMAGE = 0x00000300 # Respects the scaling method
        # of Softimage.
    FLAG_EULER = 0x00001000 # euler rotn, not quaternion

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the skeleton from given FRES."""
        super().readFromFRES(fres, offset, reader)
        self.dumpToDebugLog()
        self.dumpOffsets()

        scaleModes = ('none', 'standrd', 'maya', 'softimage')
        log.debug("Skeleton contains %d bones, %d smooth idxs, %d rigid idxs, %d extras; scale mode=%s, rotation=%s; smooth_mtx_offs=0x%X",
            self.num_bones, self.num_smooth_idxs,
            self.num_rigid_idxs, self.num_extra,
            scaleModes[(self.flags >> 8) & 3],
            'euler' if self.flags & self.FLAG_EULER else 'quaternion',
            self.smooth_mtx_offs)

        self._readBones(fres)
        self._readSmoothIdxs(fres)
        self._readSmoothMtxs(fres)

        return self

    def _readBones(self, fres):
        self.bones = []
        self.bonesByName = {}
        self.boneIdxGroups = []
        offs = self.bone_array_offs

        for i in range(self.num_bones):
            b = Bone().readFromFRES(fres, offs)
            self.bones.append(b)
            if b.name in self.bonesByName:
                log.warn("Duplicate bone name '%s'", b.name)
                self.bonesByName[b.name] = b
            offs += Bone._reader.size

        self.boneIdxGroups = Dict().readFromFile(self.fres.file,
            self.bone_idx_group_offs)

    def _readSmoothIdxs(self, fres):
        self.smooth_idxs = fres.read('h',
            pos   = self.smooth_idx_offs,
            count = self.num_smooth_idxs)
        log.debug("Smooth idxs: %s", self.smooth_idxs)

    def _readSmoothMtxs(self, fres):
        """Read the smooth matrices."""

        self.smooth_mtxs = []
        for i in range(max(self.smooth_idxs)):
            mtx = fres.read('3f', count = 4,
                pos = self.smooth_mtx_offs + (i*16*3))

            # warn about invalid values
            for y in range(4):
                for x in range(3):
                    n = mtx[y][x]
                    if math.isnan(n) or math.isinf(n):
                        log.warning("Skeleton smooth mtx %d element [%d,%d] is %s",
                            i, x, y, n)

            # replace all invalid values with zeros
            flt = lambda e: \
                0 if (math.isnan(e) or math.isinf(e)) else e
            mtx = list(map(lambda row: list(map(flt, row)), mtx))
            #mtx[3][3] = 1 # debug

            # transpose
            #m = [[0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]]
            #for y in range(4):
            #    for x in range(4):
            #        m[x][y] = mtx[y][x]
            #mtx = m

            # log values to debug
            #log.debug("Inverse mtx %d:", i)
            #for y in range(4):
            #    log.debug("  %s", ' '.join(map(
            #        lambda v: '%+3.2f' % v, mtx[y])))
            self.smooth_mtxs.append(mtx)


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
