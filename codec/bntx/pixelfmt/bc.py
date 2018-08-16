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
    r =  (pixel        & 0x1F) << 3
    g = ((pixel >>  5) & 0x3F) << 2
    b = ((pixel >> 11) & 0x1F) << 3
    return r, g, b, 0xFF


def clamp(val):
    if val > 1: return 0xFF
    if val < 0: return 0
    return int(val * 0xFF)


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

    def calcAlpha(self, alpha):
        # used by BC3, BC4, BC5
        a0, a1 = alpha[0], alpha[1]
        d = (a0, a1, 0, 0, 0, 0, 0, 0xFF)
        alpha = bytearray(bytes(d))
        for i in range(2, 6):
            if a0 > a1:
                alpha[i] = int(((8-i) * a0 + (i-1) * a1) / 7)
            else:
                alpha[i] = int(((6-i) * a0 + (i-1) * a1) / 7)
        return alpha



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

    # BC1 uses different LUT calculations than other BC formats
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
        decode  = self.decodePixel
        bpp     = self.bytesPerPixel
        data    = tex.data
        width   = int((tex.width  + 3) / 4)
        height  = int((tex.height + 3) / 4)
        pixels  = bytearray(width * height * 64)
        swizzle = tex.swizzle.getOffset

        for y in range(height):
            for x in range(width):
                offs = swizzle(x, y)
                tile = self.decodeTile(data, offs)
                alphaCh = struct.unpack_from('Q', data, offs)[0]

                toffs = 0
                for ty in range(4):
                    for tx in range(4):
                        alpha = (alphaCh >> (ty * 16 + tx * 4)) & 0xF
                        out = (x*4 + tx + (y * 4 + ty) * width * 4) * 4
                        pixels[out : out+3] = tile[toffs : toffs+3]
                        pixels[out+3] = alpha | (alpha << 4)
                        toffs += 4

        return pixels, self.depth


class BC3(TextureFormat, BCn):
    id = 0x1C
    bytesPerPixel = 16

    def decode(self, tex):
        decode = self.decodePixel
        bpp    = self.bytesPerPixel
        data   = tex.data
        width  = int((tex.width  + 3) / 4)
        height = int((tex.height + 3) / 4)
        pixels = bytearray(width * height * 64)
        swizzle = tex.swizzle.getOffset

        for y in range(height):
            for x in range(width):
                offs = swizzle(x, y)
                tile = self.decodeTile(data, offs)
                alpha = self.calcAlpha(data[offs : offs+2])
                alphaCh = struct.unpack('Q', alpha)[0]

                toffs = 0
                for ty in range(4):
                    for tx in range(4):
                        out = (x*4 + tx + (y * 4 + ty) * width * 4) * 4
                        pixels[out : out+3] = tile[toffs : toffs+3]
                        pixels[out+3] = \
                            alpha[(alphaCh >> (ty * 12 + tx * 3)) & 7]
                        toffs += 4

        return pixels, self.depth


class BC4(TextureFormat, BCn):
    id = 0x1D
    bytesPerPixel = 8

    def decode(self, tex):
        decode = self.decodePixel
        bpp    = self.bytesPerPixel
        data   = tex.data
        width  = int((tex.width  + 3) / 4)
        height = int((tex.height + 3) / 4)
        pixels = bytearray(width * height * 64)
        swizzle = tex.swizzle.getOffset

        for y in range(height):
            for x in range(width):
                offs = swizzle(x, y)
                red = self.calcAlpha(data[offs : offs+2])
                redCh = struct.unpack('Q', red)[0]

                toffs = 0
                for ty in range(4):
                    for tx in range(4):
                        out = (x*4 + tx + (y * 4 + ty) * width * 4) * 4
                        r   = red[(redCh >> (ty * 12 + tx * 3)) & 7]
                        pixels[out : out+4] = (r, r, r, 0xFF)
                        toffs += 4

        return pixels, self.depth


class BC5(TextureFormat, BCn):
    id = 0x1E
    bytesPerPixel = 16

    def decode(self, tex):
        decode   = self.decodePixel
        bpp      = self.bytesPerPixel
        data     = tex.data
        width    = int((tex.width  + 3) / 4)
        height   = int((tex.height + 3) / 4)
        pixels   = bytearray(width * height * 64)
        swizzle  = tex.swizzle.getOffset
        is_snorm = tex.fmt_dtype.name == 'SNorm'

        for y in range(height):
            for x in range(width):
                offs    = swizzle(x, y)
                red     = self.calcAlpha(data[offs : offs+2])
                redCh   = struct.unpack('Q', red)[0]
                green   = self.calcAlpha(data[offs+8 : offs+10])
                greenCh = struct.unpack('Q', green)[0]

                toffs = 0
                if is_snorm:
                    for ty in range(4):
                        for tx in range(4):
                            shift = ty * 12 + tx * 3
                            out = (x*4 + tx + (y*4 + ty)*width*4)*4
                            r   = red  [(redCh   >> shift) & 7] + 0x80
                            g   = green[(greenCh >> shift) & 7] + 0x80
                            nx = (r / 255.0) * 2 - 1
                            ny = (g / 255.0) * 2 - 1
                            nz = math.sqrt(1 - (nx*nx + ny*ny))
                            pixels[out : out+4] = (
                                clamp((nz+1) * 0.5),
                                clamp((ny+1) * 0.5),
                                clamp((nx+1) * 0.5),
                                0xFF)
                            toffs += 4
                else:
                    for ty in range(4):
                        for tx in range(4):
                            shift = ty * 12 + tx * 3
                            out = (x*4 + tx + (y*4 + ty)*width*4)*4
                            r   = red  [(redCh   >> shift) & 7]
                            g   = green[(greenCh >> shift) & 7]
                            pixels[out : out+4] = (r, r, r, g)
                            toffs += 4

        return pixels, self.depth


    def calcAlpha(self, alpha, tex):
        if tex.fmt_dtype.name != 'SNorm':
            return super().calcAlpha(alpha)

        a0, a1 = alpha[0], alpha[1]
        d = (a0, a1, 0, 0, 0, 0, 0x80, 0x7F)
        alpha = bytearray(bytes(d))
        for i in range(2, 6):
            # XXX do we need to cast here?
            if a0 > a1:
                alpha[i] = int(((8-i) * a0 + (i-1) * a1) / 7)
            else:
                alpha[i] = int(((6-i) * a0 + (i-1) * a1) / 7)
        return alpha
