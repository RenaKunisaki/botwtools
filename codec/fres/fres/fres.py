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
import struct
from structreader import readStringWithLength
from .header import Header
from .fmdl   import FMDL
from .rlt    import RLT

class FRES:
    """Represents an FRES archive."""
    def __init__(self):
        pass

    def readFromFile(self, file):
        """Read the archive from given file."""
        self.file   = file
        self.header = Header().readFromFile(file)
        log.debug("FRES version: 0x%08X", self.header.version)
        self.header.dumpToDebugLog()

        if self.header.type == 'switch':
            self.rlt = RLT().readFromFile(file, self.header.rlt_offset)
            log.debug("RLT @%06X starts at %06X",
                self.header.rlt_offset, self.rlt.data_start)
            assert self.rlt.data_start < self.file.size, \
                "RlT start 0x%X is beyond EOF 0x%X" % (
                    self.rlt.data_start, self.file.size)
            self.rlt.fres = self
            self.rlt.dumpToDebugLog()
            self.rlt.dumpOffsets()
        else:
            self.rlt = None

        self.models = []
        self.file.seek(self.header.fmdl_offset)
        for i in range(self.header.num_objects):
            pos = self.file.tell()
            log.debug("Read FMDL from 0x%X", pos)
            mdl = FMDL().readFromFRES(self)
            self.models.append(mdl)
            self.file.seek(pos + mdl.size)

        return self


    def read(self, size:(int,str)=-1, pos:int=None, count:int=1,
    use_rlt:bool=False):
        """Read data from the file.

        size:    Number of bytes, or struct format string.
        pos:     Position to seek to before reading.
        count:   Number of items to read. If not 1, returns a list.
        use_rlt: Whether to add the RLT offset (if any) to the
            file read position.

        Returns the data.
        """
        if use_rlt and (self.rlt is not None):
            # apply RLT offset
            if pos is None: pos = self.file.tell()
            log.debug("read: 0x%X + RLT 0x%X = 0x%X (size=0x%X)",
                pos,  self.rlt.data_start,
                pos + self.rlt.data_start,
                self.file.size)
            pos += self.rlt.data_start

        # validate range
        if type(size) is str: sz = struct.calcsize(size)
        else: sz = size
        if sz > 0 and pos + (sz * count) >= self.file.size:
            log.error("Reading beyond EOF "
                "(pos 0x%X size 0x%X => 0x%X, EOF is 0x%X)",
                pos, (sz*count), pos+(sz*count), self.file.size)

        # read data
        if count < 0:
            raise ValueError("Count cannot be negative")
        elif count == 0: return []
        elif count == 1:
            return self.file.read(size, pos)
        else:
            res = []
            if pos is not None: self.file.seek(pos)
            for i in range(count):
                res.append(self.file.read(size))
            return res


    def readStr(self, offset):
        """Read string (prefixed with length) from given offset."""
        return readStringWithLength(self.file, '<H', offset)