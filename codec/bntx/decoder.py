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


class BntxDecoder(Decoder):
    """Decoder for BNTX files."""
    __codec_name__ = 'BNTX'
    defaultFileExt = 'ntx'

    #def _read(self):
    #    """Read the input file, upon opening it."""
    #    self.byml = byml.Byml(self.input.read())
    #    self.root = self.byml.parse()

    #def _iter_objects(self):
    #    """Iterate over the objects in this file."""
    #    yield self.root

    #def unpack(self):
    #    """Unpack this file to `self.destPath`."""
    #    with open(self.destPath, 'wb') as file:
    #        byml_to_yml(self.root, file)
