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
        rot = Matrix([
            [1, 0,            0,           0],
            [0, math.cos(r), -math.sin(r), 0],
            [0, math.sin(r),  math.cos(r), 0],
            [0, 0,            0,           1],
        ])
        return self @ rot

    def rotateY(self, r):
        """Rotate on Y axis."""
        rot = Matrix([
            [ math.cos(r), 0, math.sin(r), 0],
            [ 0,           1, 0,           0],
            [-math.sin(r), 0, math.cos(a), 0],
            [0,            0, 0,           1],
        ])
        return self @ rot

    def rotateZ(self, r):
        """Rotate on Z axis."""
        rot = Matrix([
            [math.cos(r), -math.sin(r), 0, 0],
            [math.sin(r),  math.cos(r), 0, 0],
            [0,            0,           1, 0],
            [0,            0,           0, 1],
        ])
        return self @ rot
