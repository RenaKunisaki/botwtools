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

class Matrix(np.ndarray):
    """2-dimensional matrix of arbitrary size.

    Usually, this will be a 4x4, 4x3, or 3x3 matrix representing
    a transformation in 2D or 3D space.

    This class wraps `numpy.ndarray` and adds transformation methods.
    """

    def __new__(cls, *data):
        h = len(data)
        w = len(data[0])
        obj = super(Matrix, cls).__new__(cls, (w,h))
        for y in range(h):
            for x in range(w):
                obj[x,y] = data[y][x]
        return obj

    @staticmethod
    def I(size):
        """Create identity matrix of specified dimension."""
        d = []
        for y in range(size):
            row = []
            for x in range(size):
                row.append(1 if x == y else 0)
            d.append(row)
        return Matrix(*d)

    @staticmethod
    def Translate(size, vec):
        """Create square matrix translated by vector."""
        return Matrix.I(size).translate(vec)

    @staticmethod
    def Scale(size, vec):
        """Create square matrix scaled by vector."""
        return Matrix.I(size).scale(vec)

    def __invert__(self):
        return np.linalg.inv(self)

    def __getattr__(self, key):
        if key == 'I': return ~self
        return super().__getattr__(key)

    def translate(self, vec):
        """Translate by vector."""
        w = self.shape[0]-1
        for i, v in enumerate(vec):
            self[w,i] += v
        return self

    def scale(self, vec):
        """Scale by vector."""
        for i, v in enumerate(vec):
            self[i,i] *= v
        return self

    def rotateX(self, r):
        """Rotate on X axis."""
        rot = Matrix(
            [1, 0,            0,           0],
            [0, math.cos(r), -math.sin(r), 0],
            [0, math.sin(r),  math.cos(r), 0],
            [0, 0,            0,           1],
        )
        return self @ rot

    def rotateY(self, r):
        """Rotate on Y axis."""
        rot = Matrix(
            [ math.cos(r), 0, math.sin(r), 0],
            [ 0,           1, 0,           0],
            [-math.sin(r), 0, math.cos(r), 0],
            [0,            0, 0,           1],
        )
        return self @ rot

    def rotateZ(self, r):
        """Rotate on Z axis."""
        rot = Matrix(
            [math.cos(r), -math.sin(r), 0, 0],
            [math.sin(r),  math.cos(r), 0, 0],
            [0,            0,           1, 0],
            [0,            0,           0, 1],
        )
        return self @ rot

    def rotateXYZ(self, vec):
        """Rotate on X, Y, and Z axes."""
        # from http://www.opengl-tutorial.org/assets/faq_quaternions/index.html#Q36
        A   = math.cos(vec.x)
        B   = math.sin(vec.x)
        C   = math.cos(vec.y)
        D   = math.sin(vec.y)
        E   = math.cos(vec.z)
        F   = math.sin(vec.z)
        AD  =   A * D
        BD  =   B * D
        m0  =   C * E
        m1  =  -C * F
        m2  =   D
        m4  =  BD * E + A * F
        m5  = -BD * F + A * E
        m6  =  -B * C
        m8  = -AD * E + B * F
        m9  =  AD * F + B * E
        m10 =   A * C
        M   = Matrix(
            (m0, m1, m2,  0),
            (m4, m5, m6,  0),
            (m8, m9, m10, 0),
            (0,  0,  0,   1),
        )
        return self @ M
