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
from structreader import StructReader, BinaryObject
from .fresobject import FresObject
from codec.base.types import Offset, Offset64, StrOffs, Padding, Flags, Vec3f, Vec4f
from vmath import Vec3, Vec4

class Bone(FresObject):
    """A bone in an FSKL."""
    # offsets in this struct are relative to the beginning of
    # the FRES file.
    # I'm assuming they're 64-bit.
    _reader = StructReader(
        StrOffs('name'),
        ('5I',  'unk04'),
        ('H',  'bone_idx'),
        ('h',  'parent'),
        ('h',  'smooth_mtx_idx'),
        ('h',  'rigid_mtx_idx'),
        ('h',  'billboard_idx'),
        ('H',  'udata_count'),
        Flags('flags', {
            'VISIBLE': 0x00000001,
            'EULER':   0x00001000, # use euler rotn, not quaternion
            'BB_CHILD':0x00010000, # child billboarding
            'BB_WORLD_VEC':0x00020000, # World View Vector.
                # The Z axis is parallel to the camera.
            'BB_WORLD_POINT':0x00030000, # World View Point.
                # The Z axis is equal to the direction the camera
                # is pointing to.
            'BB_SCREEN_VEC':0x00040000, # Screen View Vector.
                # The Z axis is parallel to the camera, the Y axis is
                # equal to the up vector of the camera.
            'BB_SCREEN_POINT':0x00050000, # Screen View Point.
                # The Z axis is equal to the direction the camera is
                # pointing to, the Y axis is equal to the up vector of
                # the camera.
            'BB_Y_VEC':0x00060000, # Y-Axis View Vector.
                # The Z axis has been made parallel to the camera view
                # by rotating the Y axis.
            'BB_Y_POINT':0x00070000, # Y-Axis View Point.
                # The Z axis has been made equal to the direction
                # the camera is pointing to by rotating the Y axis.
            'SEG_SCALE_COMPENSATE':0x00800000, # Segment scale
                # compensation. Set for bones scaled in Maya whose
                # scale is not applied to child bones.
            'UNIFORM_SCALE': 0x01000000, # Scale uniformly.
            'SCALE_VOL_1':   0x02000000, # Scale volume by 1.
            'NO_ROTATION':   0x04000000,
            'NO_TRANSLATION':0x08000000,
            # same as previous but for hierarchy of bones
            'GRP_UNIFORM_SCALE': 0x10000000,
            'GRP_SCALE_VOL_1':   0x20000000,
            'GRP_NO_ROTATION':   0x40000000,
            'GRP_NO_TRANSLATION':0x80000000,
        }),
        Vec3f('scale'),
        Vec4f('rot'),
        Vec3f('pos'),
        size = 80,
    )

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the bone from given FRES."""
        super().readFromFRES(fres, offset, reader)
        #self.s60  = readStringWithLength(file, '<H', self.unk60)
        #self.s70  = readStringWithLength(file, '<H', self.unk70)
        #self.s88  = readStringWithLength(file, '<H', self.unk88)

        flagStr=[]
        names=(
            'VISIBLE',
            'EULER',
            'BB_CHILD',
            'BB_WORLD_VEC',
            'BB_WORLD_POINT',
            'BB_SCREEN_VEC',
            'BB_SCREEN_POINT',
            'BB_Y_VEC',
            'BB_Y_POINT',
            'SEG_SCALE_COMPENSATE',
            'UNIFORM_SCALE',
            'SCALE_VOL_1',
            'NO_ROTATION',
            'NO_TRANSLATION',
            'GRP_UNIFORM_SCALE',
            'GRP_SCALE_VOL_1',
            'GRP_NO_ROTATION',
            'GRP_NO_TRANSLATION',
        )
        for name in names:
            if self.flags[name]:
                flagStr.append(name)

        log.debug("Bone %d: '%s', parent=%d smooth=%d rigid=%d billboard=%d udata=%d scale=%s rot=%s pos=%s flags=0x%08X  %s",
            self.bone_idx, self.name, self.parent,
            self.smooth_mtx_idx, self.rigid_mtx_idx,
            self.billboard_idx, self.udata_count,
            self.scale, self.rot, self.pos,
            self.flags, ', '.join(flagStr))

        #log.debug("Bone name  = '%s'", self.name)
        #log.debug("Bone s60   = '%s'", self.s60)
        #log.debug("Bone s70   = '%s'", self.s70)
        #log.debug("Bone s88   = '%s'", self.s88)

        #self.dumpToDebugLog()
        return self


    def validate(self):
        super().validate()
        return True
