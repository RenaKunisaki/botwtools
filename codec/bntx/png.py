# adapted from https://stackoverflow.com/a/25835368
""" Converts a list of list into gray-scale PNG image. """
__copyright__ = "Copyright (C) 2014 Guido Draheim"
__licence__ = "Public Domain"

import logging; log = logging.getLogger(__name__)
import zlib
import struct

def I1(value):
    return struct.pack("!B", value & (2**8-1))
def I4(value):
    return struct.pack("!I", value & (2**32-1))

class PNG:
    class ColorType:
        GREYSCALE = 0
        TRUE_COLOR = 2
        INDEXED_COLOR = 3
        GREYSCALE_ALPHA = 4
        TRUE_COLOR_ALPHA = 6

    class CompressionType:
        ZLIB = 0

    class FilterType:
        ADAPTIVE = 0

    def __init__(self, pixels=None, width=1, height=1, bpp=8):
        self.width  = width
        self.height = height
        self.bpp    = bpp # bits per pixel
        self.pixels = pixels
        self.color_type = self.ColorType.TRUE_COLOR_ALPHA
        self.compression_type = self.CompressionType.ZLIB
        self.filter_type = self.FilterType.ADAPTIVE
        self.interlaced = False

    def writeToFile(self, file):
        self.writeMagic(file)
        self.writeIHDR(file)
        self.writeIDAT(file)
        self.writeIEND(file)

    def writeMagic(self, buf):
        buf.write(b"\x89PNG\r\n\x1A\n")

    def makeBlock(self, name, data):
        block = name.encode('ascii') + data
        return I4(len(data)) + block + I4(zlib.crc32(block))

    def writeIHDR(self, buf):
        IHDR = I4(self.width) + I4(self.height) + I1(self.bpp)
        IHDR += I1(self.color_type) + I1(self.compression_type)
        IHDR += I1(self.filter_type) + I1(1 if self.interlaced else 0)
        buf.write(self.makeBlock('IHDR', IHDR))

    def writeIDAT(self, buf):
        data = self.pixels
        pad  = (self.width * self.height * 4) - len(data)
        if pad > 0:
            data = self.pixels + (b'\0' * pad)
        idx = 0
        raw = b""
        for y in range(self.height):
            raw += b"\0" # no filter for this scanline
            for x in range(self.width):
                c = data[idx:idx+4]
                raw += c
                idx += 4
        compressor = zlib.compressobj()
        compressed = compressor.compress(raw)
        compressed += compressor.flush() #!!
        log.debug("PNG data = %d bytes compressed to %d",
            len(data), len(compressed))
        buf.write(self.makeBlock('IDAT', compressed))

    def writeIEND(self, buf):
        buf.write(self.makeBlock('IEND', b''))
