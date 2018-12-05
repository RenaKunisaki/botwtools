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
import numpy as np
from .vec3 import Vec3
from .vec4 import Vec4
from .matrix import Matrix

class Quaternion(Vec4):
    """A quaternion."""

    @staticmethod
    def fromAxisAngle(axis:Vec3, angle):
        """Construct from axis angle."""

        return Quaternion(
            x = axis.x * math.sin(angle/2),
            y = axis.y * math.sin(angle/2),
            z = axis.z * math.sin(angle/2),
            w =          math.cos(angle/2),
        )

    @staticmethod
    def fromEulerAngles(rot:Vec3):
        """Construct from a Vec3 of X, Y, Z rotations."""
        x = Quaternion.fromAxisAngle(Vec3.UnitX, rot.x)
        y = Quaternion.fromAxisAngle(Vec3.UnitY, rot.y)
        z = Quaternion.fromAxisAngle(Vec3.UnitZ, rot.z)
        #q = z * y * x
        q = x * y * z
        if q.w < 0: q *= -1
        #log.debug("Q from %s: %s * %s * %s => %s",
        #    rot, z, y, x, q)
        return q

    def toMatrix(self):
        """Build a 4x4 matrix from this quaternion."""
        x,  y,  z, w = self.x, self.y, self.z, self.w
        x2, y2, z2   = x+x,  y+y,  z+z
        xx, xy, xz   = x*x2, x*y2, x*z2
        yy, yz, zz   = y*y2, y*z2, z*z2
        wx, wy, wz   = w*x2, w*y2, w*z2
        return Matrix(
            (1-(yy+zz),     xy+wz,     xz-wy,  0),
            (   xy-wz,   1-(xx+zz),    yz+wx,  0),
            (   xz+wy,      yz-wx,  1-(xx+yy), 0),
            (0,          0,         0,         1),
        )

    def __mul__(self, other):
        C = type(self)
        if type(other) in (int, float):
            return C(self[0]*other, self[1]*other, self[2]*other,
                self[3]*other)
        else:
            ax, ay, az, aw = self [0], self [1], self [2], self [3]
            bx, by, bz, bw = other[0], other[1], other[2], other[3]
            return C(
                aw * bx + ax * bw + ay * bz - az * by,  # i
                aw * by - ax * bz + ay * bw + az * bx,  # j
                aw * bz + ax * by - ay * bx + az * bw,  # k
                aw * bw - ax * bx - ay * by - az * bz,  # 1
            )
