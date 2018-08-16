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
#
# This file also contains code from byml-v2 which is
# published under the GPLv2+ license.

import logging; log = logging.getLogger(__name__)
import io
import os
import sys
import struct
from filereader import FileReader
from ..base import Decoder, UnsupportedFileTypeError, BinInput, TxtOutput
from . import bntx
from .png import PNG


class BntxDecoder(Decoder):
    """Decoder for BNTX files."""
    __codec_name__ = 'BNTX'
    defaultFileExt = 'ntx'

    def _read(self):
        """Read the input file, upon opening it."""
        self.bntx = bntx.BNTX().readFromFile(self.input)

    def _iter_objects(self):
        """Iterate over the objects in this file."""
        yield self.bntx

    def printList(self, dest:TxtOutput=sys.stdout):
        """Print nicely formatted list of this file's objects."""
        print("%3d textures" % len(self.bntx.textures))
        print("  Num   Dimensions Fmt  M S Name")
        for i, tex in enumerate(self.bntx.textures):
            print('  %3d: %4dx%4dx%d %-4s %d %d "%s"' % (i,
                tex.width, tex.height, tex.depth,
                type(tex.fmt_type).__name__,
                tex.mipmap_cnt, tex.multisample_cnt,
                tex.name))
        print("M=mipmap count, S=multisample count")

    def unpack(self):
        """Unpack this file to `self.destPath`."""
        for i, tex in enumerate(self.bntx.textures):
            pixels, depth = tex.decode()
            log.debug("Texture depth is %d, fmt %s", depth,
                type(tex.fmt_type).__name__)

            # dump raw data
            #with self.mkfile(tex.name + '.data') as file:
            #    file.write(pixels)

            png = PNG(width=tex.width, height=tex.height,
                pixels=pixels, bpp=depth)
            with self.mkfile(tex.name + '.png') as file:
                png.writeToFile(file)
