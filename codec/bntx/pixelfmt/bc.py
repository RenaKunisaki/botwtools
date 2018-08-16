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
from .base import TextureFormat
from .swizzle import Swizzle


def unpackRGB565(pixel):
    b =  (pixel        & 0x1F) << 3
    g = ((pixel >>  5) & 0x3F) << 2
    r = ((pixel >> 11) & 0x1F) << 3
    return r, g, b, 0xFF


class BCn:
    def decodeTile(self, data, offs):
        clut = []
        c0, c1, idxs = struct.unpack_from('HHI', data, offs)
        clut.append(unpackRGB565(c0))
        clut.append(unpackRGB565(c1))
        clut.append(self.calcCLUT2(clut[0], clut[1], c0, c1))
        clut.append(self.calcCLUT3(clut[0], clut[1], c0, c1))

        idxshift = 0
        output = bytearray(4*4*4)
        out = 0
        for ty in range(4):
            for tx in range(4):
                i = (idxs >> idxshift) & 3
                output[out : out+4] = clut[i]
                idxshift += 2
                out += 4
        return output

    def calcCLUT2(self, lut0, lut1, c0, c1):
        r = int((2 * lut0[0] + lut1[0]) / 3)
        g = int((2 * lut0[1] + lut1[1]) / 3)
        b = int((2 * lut0[2] + lut1[2]) / 3)
        return r, g, b, 0xFF

    def calcCLUT3(self, lut0, lut1, c0, c1):
        r = int((2 * lut0[0] + lut1[0]) / 3)
        g = int((2 * lut0[1] + lut1[1]) / 3)
        b = int((2 * lut0[2] + lut1[2]) / 3)
        return r, g, b, 0xFF



class BC1(TextureFormat, BCn):
    id = 0x1A
    bytesPerPixel = 8

    def decode(self, tex):
        decode  = self.decodePixel
        bpp     = self.bytesPerPixel
        data    = tex.data
        width   = int((tex.width  + 3) / 4)
        height  = int((tex.height + 3) / 4)
        pixels  = bytearray(width * height * 64)
        swizzle = tex.swizzle.getOffset

        log.debug("%d bytes/pixel, %dx%d = %d, len = %d",
            bpp, width, height, width * height * bpp,
            len(data))

        for y in range(height):
            for x in range(width):
                offs = swizzle(x, y)
                tile = self.decodeTile(data, offs)

                toffs = 0
                for ty in range(4):
                    for tx in range(4):
                        out = (x*4 + tx + (y * 4 + ty) * width * 4) * 4
                        pixels[out : out+4] = tile[toffs : toffs+4]
                        toffs += 4

        return pixels, self.depth

    def calcCLUT2(self, lut0, lut1, c0, c1):
        if c0 > c1:
            r = int((2 * lut0[0] + lut1[0]) / 3)
            g = int((2 * lut0[1] + lut1[1]) / 3)
            b = int((2 * lut0[2] + lut1[2]) / 3)
        else:
            r = (lut0[0] + lut1[0]) >> 1
            g = (lut0[1] + lut1[1]) >> 1
            b = (lut0[2] + lut1[2]) >> 1
        return r, g, b, 0xFF

    def calcCLUT3(self, lut0, lut1, c0, c1):
        if c0 > c1:
            r = int((2 * lut0[0] + lut1[0]) / 3)
            g = int((2 * lut0[1] + lut1[1]) / 3)
            b = int((2 * lut0[2] + lut1[2]) / 3)
            return r, g, b, 0xFF
        else:
            return 0, 0, 0, 0

class BC2(TextureFormat, BCn):
    id = 0x1B
    bytesPerPixel = 16

    def decode(self, tex):
        decode = self.decodePixel
        bpp    = self.bytesPerPixel
        data   = tex.data
        width  = int((tex.width  + 3) / 4)
        height = int((tex.height + 3) / 4)
        pixels = bytearray(width * height * (self.depth >> 3))
        swizzle = tex.swizzle.getOffset

        for y in range(height):
            for x in range(width):
                offs = swizzle(x, y)
                tile = self.decodeTile(data, offs)
                alphaLo, alphaHi = struct.unpack_from('ii', data, offs)
                alphaCh = alphaLo | (alphaHi << 32)
                # XXX can probably do: alphaCh = struct.unpack_from('Q')...

                toffs = 0
                for ty in range(4):
                    for tx in range(4):
                        alpha = (alphaCh >> (ty * 16 + tx * 4)) & 0xF
                        out = (x*4 + tx + (y * 4 + ty) * width * 4) * 4
                        pixels[out : out+3] = tile[toffs : toffs+3]
                        pixels[out+3] = alpha | (alpha << 4)
                        toffs += 4

        return pixels, self.depth
