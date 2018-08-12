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

        if self.header.type == 'switch':
            self.rlt = RLT().readFromFile(file, self.header.rlt_offset)
            log.debug("RLT @%06X starts at %06X",
                self.header.rlt_offset, self.rlt.data_start)
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

    def readStr(self, offset):
        """Read string (prefixed with length) from given offset."""
        return readStringWithLength(self.file, '<H', offset)
