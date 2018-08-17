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
from .fresobject import FresObject
from codec.base.types import Offset, Offset64, StrOffs, Padding
from structreader import StructReader, BinaryObject


class EmbeddedFile(FresObject):
    """Generic file embedded in FRES archive."""
    _reader = StructReader(
        Offset64('data_offset'),
        ('I',    'size'),
        Padding(4),
        size = 0x10,
    )

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the archive from given FRES."""
        super().readFromFRES(fres, offset, reader)

        self.dumpToDebugLog()
        #self.dumpOffsets()

        return self


    def toData(self):
        return self.fres.file.read(self.size, self.data_offset)
