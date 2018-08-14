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
from structreader import StructReader, BinaryObject

class SFATNode(BinaryObject):
    """SARC file SFAT file node."""
    _reader = StructReader(
        ('I',  'name_hash'), # filename hash
        ('I',  'file_attrs'),
        ('I',  'data_start'), # file data offs relative to SARC header data_offset
        ('I',  'data_end'),
    )

    def readFromFile(self, file):
        """Read the node from the given file."""
        super().readFromFile(file)
        if self.file_attrs & 0x01000000:
            self.name_offset = (self.file_attrs & 0xFFFF) * 4
        else:
            self.name_offset = None
        return self


    def validate(self):
        assert self.data_start <= self.data_end, \
            "File size is negative"
        return True
