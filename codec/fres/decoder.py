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
import sys
import struct
from ..base import ArchiveDecoder, FileReader, UnsupportedFileTypeError, TxtOutput
from ..base.types import Path, BinInput, BinOutput, TxtOutput, fopenMode
from .fres import FRES


class FresDecoder(ArchiveDecoder):
    """Decoder for FRES archive."""
    __codec_name__ = 'FRES'

    def _read(self):
        """Read the input file, upon opening it."""
        self.archive = FRES().readFromFile(self.input)
        log.debug("FRES contains %d models", len(self.archive.models))

    def _iter_objects(self):
        """Iterate over the objects in this file."""
        return iter(self.archive.models)

    def _get_num_objects(self) -> (int, None):
        """Get number of objects in this file.

        Returns None if not known.
        """
        return self.archive.header.num_objects

    def printList(self, dest:TxtOutput=sys.stdout):
        """Print nicely formatted list of this file's objects."""
        print("Models:", self.numObjects)
        for i, obj in enumerate(self.objects):
            print(i, obj.name)
            for bone in obj.skeleton.bones:
                print("  Bone:", bone.name)
            for mat in obj.fmats:
                print(" Material:", mat.name)
            for vtx in obj.fvtxs:
                print(" Vtx:", vtx)
            for shp in obj.fshps:
                print(" Shape:", shp.name)


    def unpack(self):
        """Unpack this file to `self.destPath`."""
        nobj = len(self.archive.models)
        for i, obj in enumerate(self.archive.models):
            name = 'FMDL%d.bin' % i
            log.info("[%3d/%3d] Extracting %s...", i+1, nobj, name)
            self.input.seek(obj._file_offset)
            self.writeFile(name, self.input.read(obj._reader._dataSize))
