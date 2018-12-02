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
        q = z * y * x
        if q.w < 0: q *= -1
        return q

    def toMatrix(self):
        """Build a 4x4 matrix from this quaternion."""
        # converted from: http://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToMatrix/index.htm

        qx  = self.x
        qy  = self.y
        qz  = self.z
        qw  = self.w
        sqw = qw * qw
        sqx = qx * qx
        sqy = qy * qy
        sqz = qz * qz

        # invs (inverse square length) is only required if quaternion is not already normalised
        invs = 1 / (sqx + sqy + sqz + sqw)
        m00  = ( sqx - sqy - sqz + sqw)*invs # since sqw + sqx + sqy + sqz =1/invs*invs
        m11  = (-sqx + sqy - sqz + sqw)*invs
        m22  = (-sqx - sqy + sqz + sqw)*invs

        tmp1 = qx*qy
        tmp2 = qz*qw
        m10  = 2.0 * (tmp1 + tmp2)*invs
        m01  = 2.0 * (tmp1 - tmp2)*invs

        tmp1 = qx*qz
        tmp2 = qy*qw
        m20  = 2.0 * (tmp1 - tmp2)*invs
        m02  = 2.0 * (tmp1 + tmp2)*invs
        tmp1 = qy*qz
        tmp2 = qx*qw
        m21  = 2.0 * (tmp1 + tmp2)*invs
        m12  = 2.0 * (tmp1 - tmp2)*invs

        return Matrix(
            (m00, m01, m02, 0),
            (m10, m11, m12, 0),
            (m20, m21, m22, 0),
            (0,   0,   0,   1),
        )
