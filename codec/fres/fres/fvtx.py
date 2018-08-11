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
from structreader import StructReader, BinaryObject, readStringWithLength

class FVTX(BinaryObject):
    """A FVTX in an FSKL."""
    # offsets in this struct are relative to the beginning of
    # the FRES file.
    # I'm assuming they're 64-bit.
    _reader = StructReader(
        ('4s', 'magic'),  # 'FVTX'
        ('B',  'num_attrs'), # num attributes
        ('B',  'num_bufs'),  # num buffers
        ('H',  'sec_idx'), # section index
        ('I',  'num_vtxs'),  # num vertices
        ('B',  'skin_cnt'),# vtx skin count
        ('3B', 'padding0D'),
        ('i',  'attrArrayOffs'), # offset to first elem in attribute array
        ('i',  'attrGroupOffs'), # attr index group offset
        ('i',  'bufArrayOffs'), # offset to first elem in buffer array
        ('I',  'user_ptr'), # always 0, changed at runtime
    )

    def readFromFile(self, file, offset=None, reader=None):
        """Read the FVTX from given file."""
        log.debug("Reading FVTX from 0x%08X", offset)
        super().readFromFile(file, offset, reader)

        self.dumpToDebugLog()
        return self


    def validate(self):
        return True
