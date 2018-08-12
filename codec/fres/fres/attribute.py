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
from structreader import StructReader, BinaryObject

class Attribute(BinaryObject):
    """An attribute in a FRES."""
    _reader = StructReader(
        ('I',  'name_offset'), # u16 len, str
        ('I',  'unk04'),
        ('H',  'format'),
        ('H',  'unk0A'),
        ('H',  'buf_offs'),
        ('H',  'buf_idx'),
    )

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the attribute from given FRES."""
        super().readFromFile(fres.file, offset, reader)
        self.fres = fres
        self.name = fres.readStr(self.name_offset)
        log.debug("Attr name = '%s', fmt=%04X", self.name, self.format)

        self.dumpToDebugLog()
        return self


    def validate(self):
        super().validate()
        return True
