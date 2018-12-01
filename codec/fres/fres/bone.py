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
from codec.base.types import Offset, Offset64, StrOffs, Padding

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
        ('I',  'flags'),
        ('f',  'scaleX'),
        ('f',  'scaleY'),
        ('f',  'scaleZ'),
        ('f',  'rotX'),
        ('f',  'rotY'),
        ('f',  'rotZ'),
        ('f',  'rotW'),
        ('f',  'posX'),
        ('f',  'posY'),
        ('f',  'posZ'),
        size = 80,
    )

    FLAG_VISIBLE     =0x00000001
    FLAG_EULER       =0x00001000 # use euler rotn, not quaternion
    FLAG_BB_NONE     =0x00000000 # no billboarding
    FLAG_BB_CHILD    =0x00010000 # child billboarding
    FLAG_BB_WORLD_VEC=0x00020000 # World View Vector.
        # The Z axis is parallel to the camera.
    FLAG_BB_WORLD_POINT=0x00030000 # World View Point.
        # The Z axis is equal to the direction the camera
        # is pointing to.
    FLAG_BB_SCREEN_VEC=0x00040000 # Screen View Vector.
        # The Z axis is parallel to the camera, the Y axis is
        # equal to the up vector of the camera.
    FLAG_BB_SCREEN_POINT=0x00050000 # Screen View Point.
        # The Z axis is equal to the direction the camera is
        # pointing to, the Y axis is equal to the up vector of
        # the camera.
    FLAG_BB_Y_VEC=0x00060000 # Y-Axis View Vector.
        # The Z axis has been made parallel to the camera view
        # by rotating the Y axis.
    FLAG_BB_Y_POINT=0x00070000 # Y-Axis View Point.
        # The Z axis has been made equal to the direction
        # the camera is pointing to by rotating the Y axis.
    FLAG_SEG_SCALE_COMPENSATE=0x00800000 # Segment scale
        # compensation. Set for bones scaled in Maya whose
        # scale is not applied to child bones.
    FLAG_UNIFORM_SCALE =0x01000000 # Scale uniformly.
    FLAG_SCALE_VOL_1   =0x02000000 # Scale volume by 1.
    FLAG_NO_ROTATION   =0x04000000
    FLAG_NO_TRANSLATION=0x08000000
    # same as previous but for hierarchy of bones
    FLAG_GRP_UNIFORM_SCALE =0x10000000
    FLAG_GRP_SCALE_VOL_1   =0x20000000
    FLAG_GRP_NO_ROTATION   =0x40000000
    FLAG_GRP_NO_TRANSLATION=0x80000000


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
            'BB_NONE',
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
            val = getattr(self, 'FLAG_'+name)
            if self.flags & val:
                flagStr.append(name)

        log.debug("Bone %d: '%s', parent=%d smooth=%d rigid=%d billboard=%d udata=%d scale=%+2.1f %+2.1f %+2.1f rot=%+2.1f %+2.1f %+2.1f %+2.1f pos=%+2.1f %+2.1f %+2.1f flags=0x%08X  %s",
            self.bone_idx, self.name, self.parent,
            self.smooth_mtx_idx, self.rigid_mtx_idx,
            self.billboard_idx, self.udata_count,
            self.scaleX, self.scaleY, self.scaleZ,
            self.rotX, self.rotY, self.rotZ, self.rotW,
            self.posX, self.posY, self.posZ,
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
