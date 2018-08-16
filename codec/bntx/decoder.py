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
import struct
from filereader import FileReader
from ..base import Decoder, UnsupportedFileTypeError, BinInput
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

    def unpack(self):
        """Unpack this file to `self.destPath`."""
        for i, tex in enumerate(self.bntx.textures):
            pixels, depth = tex.decode()
            log.debug("Texture depth is %d", depth)
            with self.mkfile(tex.name + '.data') as file:
                file.write(pixels)
            png = PNG(width=tex.width, height=tex.height,
                pixels=pixels, bpp=depth)
            log.debug("Writing PNG, size %dx%d", tex.width, tex.height)
            with self.mkfile(tex.name + '.png') as file:
                png.writeToFile(file)
