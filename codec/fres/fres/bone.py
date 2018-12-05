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
from vmath import Matrix, Vec3, Vec4, Quaternion
import math

class Bone(FresObject):
    """A bone in an FSKL."""
    # offsets in this struct are relative to the beginning of
    # the FRES file.
    # I'm assuming they're 64-bit.
    _reader = StructReader(
        StrOffs('name'),
        ('5I',  'unk04'),
        ('H',  'bone_idx'),
        ('h',  'parent_idx'),
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
        self.parent = None # to be set by the FSKL
        self.fskl   = None # to be set by the FSKL

        #self.rot *= -1
        #self.rot.x %= (2*math.pi)
        #self.rot.y %= (2*math.pi)
        #self.rot.z %= (2*math.pi)

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
        self._flagStr = ' '.join(flagStr)

        #log.debug("Bone %d: '%s', parent=%d smooth=%d rigid=%d billboard=%d udata=%d scale=%s rot=%s pos=%s flags=0x%08X  %s",
        #    self.bone_idx, self.name, self.parent_idx,
        #    self.smooth_mtx_idx, self.rigid_mtx_idx,
        #    self.billboard_idx, self.udata_count,
        #    self.scale, self.rot, self.pos,
        #    self.flags['_raw'], ', '.join(flagStr))

        #log.debug("Bone name  = '%s'", self.name)
        #log.debug("Bone s60   = '%s'", self.s60)
        #log.debug("Bone s70   = '%s'", self.s70)
        #log.debug("Bone s88   = '%s'", self.s88)

        #self.dumpToDebugLog()
        return self


    def validate(self):
        super().validate()
        return True


    def computeTransform(self):
        """Compute final transformation matrix."""
        T = self.pos
        S = self.scale
        R = self.rot

        # why have these flags instead of just setting the
        # values to 0/1? WTF Nintendo.
        # they seem to only be set when the values already are
        # 0 (or 1, for scale) anyway.
        #if self.flags['NO_ROTATION']:    R = Vec4(0, 0, 0, 1)
        #if self.flags['NO_TRANSLATION']: T = Vec3(0, 0, 0)
        #if self.flags['SCALE_VOL_1']:    S = Vec3(1, 1, 1)
        if self.flags['SEG_SCALE_COMPENSATE']:
            # apply inverse of parent's scale
            if self.parent:
                S *= 1 / self.parent.scale
            else:
                log.error("Bone '%s' has flag SEG_SCALE_COMPENSATE but no parent", self.name)
        # no idea what "scale uniformly" actually means.
        # XXX billboarding, rigid mtxs, if ever used.

        # Build matrices from these transformations.
        T = Matrix.Translate(4, T)
        S = Matrix.Scale    (4, S)
        R = Quaternion.fromEulerAngles(R).toMatrix()
        if self.parent:
            P = self.parent.computeTransform()
        else: P = Matrix.I(4)
        M = Matrix.I(4)

        # multiply by the smooth matrix if any
        #if self.smooth_mtx_idx >= 0:
        #    mtx = self.fskl.smooth_mtxs[self.smooth_mtx_idx]
        #    # convert 4x3 to 4x4
        #    mtx = Matrix(mtx[0], mtx[1], mtx[2], (0, 0, 0, 1))
        #    M = M @ mtx

        # apply the transformations
        # SRTP is the order used by BFRES-Viewer...
        #M = M @ T @ R @ S @ P
        M = M @ S @ R @ T @ P
        #M = M @ P @ T @ R @ S
        #M = M @ P @ S @ R @ T

        return M
