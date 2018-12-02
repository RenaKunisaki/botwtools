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

class Vec3(np.ndarray):
    """3-dimensional vector.

    This class wraps `numpy.ndarray` and adds some vector math
    methods which amazingly don't seem to be built in.
    """
    def __new__(cls, x=0, y=0, z=0):
        obj = super(Matrix, cls).__new__(cls, (3,))
        obj[0] = x
        obj[1] = y
        obj[2] = z
        return obj

    def dot(self, other):
        """Dot product."""
        return (
            (self[0] * other[0]) +
            (self[1] * other[1]) +
            (self[2] * other[2]))

    def cross(self, other):
        """Cross product."""
        return (
            ((self[1] * other[2]) - (self[2] * other[1])) +
            ((self[2] * other[0]) - (self[0] * other[2])) +
            ((self[0] * other[1]) - (self[1] * other[0])) )

    def __str__(self):
        return "(%3.2f, %3.2f, %3.2f)" % (self[0], self[1], self[2])

    def __repr__(self):
        return "Vec3(%f, %f, %f)" % (self[0], self[1], self[2])

    def __getitem__(self, key):
        if key == 0 or key in 'xX': return self[0]
        if key == 1 or key in 'yY': return self[1]
        if key == 2 or key in 'zZ': return self[2]
        # XXX slice
        raise KeyError(key)

    def __setitem__(self, key, val):
        if key == 0 or key in 'xX': self[0] = val
        if key == 1 or key in 'yY': self[1] = val
        if key == 2 or key in 'zZ': self[2] = val
        # XXX slice
        raise KeyError(key)
        return self

    def __getattr__(self, key):
        if key == 'length':
            return math.sqrt(
                (self[0] * self[0])+
                (self[1] * self[1])+
                (self[2] * self[2]))
        elif key == 'normal':
            return self / self.length
        else:
            raise AttributeError(key)

    def __eq__(self, other):
        return (self[0] == other[0]
            and self[1] == other[1]
            and self[2] == other[2])

    def __add__(self, other):
        return Vec3(self[0]+other[0], self[1]+other[1], self[2]+other[2])

    def __sub__(self, other):
        return Vec3(self[0]-other[0], self[1]-other[1], self[2]-other[2])

    def __mul__(self, other):
        if type(other) in (int, float):
            return Vec3(self[0]*other, self[1]*other, self[2]*other)
        else:
            return Vec3(self[0]*other[0], self[1]*other[1], self[2]*other[2])

    def __truediv__(self, other):
        if type(other) in (int, float):
            return Vec3(self[0]/other, self[1]/other, self[2]/other)
        else:
            return Vec3(self[0]/other[0], self[1]/other[1], self[2]/other[2])

    def __floordiv__(self, other):
        if type(other) in (int, float):
            return Vec3(self[0]//other, self[1]//other, self[2]//other)
        else:
            return Vec3(self[0]//other[0], self[1]//other[1], self[2]//other[2])

    def __iadd__(self, other):
        self[0] += other[0]
        self[1] += other[1]
        self[2] += other[2]
        return self

    def __isub__(self, other):
        self[0] -= other[0]
        self[1] -= other[1]
        self[2] -= other[2]
        return self

    def __imul__(self, other):
        if type(other) in (int, float):
            self[0] *= other
            self[1] *= other
            self[2] *= other
        else:
            self[0] *= other[0]
            self[1] *= other[1]
            self[2] *= other[2]
        return self

    def __itruediv__(self, other):
        if type(other) in (int, float):
            self[0] /= other
            self[1] /= other
            self[2] /= other
        else:
            self[0] /= other[0]
            self[1] /= other[1]
            self[2] /= other[2]
        return self

    def __ifloordiv__(self, other):
        if type(other) in (int, float):
            self[0] //= other
            self[1] //= other
            self[2] //= other
        else:
            self[0] //= other[0]
            self[1] //= other[1]
            self[2] //= other[2]
        return self

    def __neg__(self):
        return Vec3(-self[0], -self[1], -self[2])