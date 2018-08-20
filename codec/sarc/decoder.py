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
import io
import sys
import struct
from filereader import FileReader
from ..base import ArchiveDecoder, UnsupportedFileTypeError, TxtOutput
from .reader import SARC

class SarcDecoder(ArchiveDecoder):
    """Decoder for SARC archive."""
    __codec_name__ = 'SARC'

    def _read(self):
        """Read the input file, upon opening it."""
        self.archive = SARC().readFromFile(self.input)

    def _iter_objects(self):
        """Iterate over the objects in this file."""
        return iter(self.archive.files)

    def _get_num_objects(self) -> (int, None):
        """Get number of objects in this file.

        Returns None if not known.
        """
        return self.archive.fatHeader.node_count

    def printList(self, dest:TxtOutput=sys.stdout):
        """Print nicely formatted list of this file's objects."""
        print("Files:", self.numObjects)
        print("NameHash  FileSize Name")
        for obj in self.objects:
            print("%08X %9d %s" % (obj.name_hash, obj.size, obj.name))

    def toString(self):
        """Return pretty string describing this object."""
        return "SARC archive containing %d files" % self.numObjects
