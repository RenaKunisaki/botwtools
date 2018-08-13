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
from .fresobject import FresObject
from .types import Offset, Offset64, StrOffs, Padding

class Attribute(FresObject):
    """An attribute in a FRES."""
    _reader = StructReader(
        StrOffs('name'),
        ('I',  'unk04'),
        ('H',  'format'),
        Padding(2),
        ('H',  'buf_offs'),
        ('H',  'buf_idx'),
        size = 0x10,
    )

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the attribute from given FRES."""
        super().readFromFRES(fres, offset, reader)
        #log.debug("Attr name = '%s', fmt=%04X", self.name, self.format)
        #self.dumpToDebugLog()
        return self


    def validate(self):
        super().validate()
        return True
