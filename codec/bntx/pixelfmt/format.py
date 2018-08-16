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
import struct

# define texture formats



class BC1(TextureFormat):
    id = 0x1A
    bytesPerPixel = 4

    def decode(self, pixel):
        pixel = struct.unpack('H', pixel)
        r =  (pixel        & 0x1F) << 3
        g = ((pixel >>  5) & 0x3F) << 2
        b = ((pixel >> 11) & 0x1F) << 3
        a = 0xFF
        return r, g, b, a


classes = (R5G6B5, R8G8, R16, R8G8B8A8, R11G11B10, R32)
for cls in classes:
    fmts[cls.id] = cls
