import logging; log = logging.getLogger(__name__)
import struct
from ..base import TextureFormat


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
