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

import logging; log = logging.getLogger()
import io
import os
import sys
import struct
from .decoder import Decoder
from .types import Path, BinInput, BinOutput, TxtOutput, fopenMode

class ArchiveDecoder(Decoder):
    """Base class for decoders for archive files (files which
    may contain more than one file).
    """
    @classmethod
    def suggestOutputName(cls, path:Path) -> Path:
        """Given the path of the input file,
        suggest a path for the output file.
        """
        path, ext = os.path.splitext(path)
        return path + '/'

    def unpack(self):
        nobj = self.numObjects
        for i, obj in enumerate(self.objects):
            name = getattr(obj, 'name', '%d.bin' % i)
            log.info("[%3d/%3d] Extracting %s...", i+1, nobj, name)
            self.writeFile(name, obj.read())
