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
from .types import Offset, Offset64, StrOffs, Padding
from structreader import StructReader, BinaryObject

class StringTable(FresObject):
    """FRES string table."""
    _magic = b'_STR'
    _reader = StructReader(
        ('4s',   'magic'),
        ('I',    'unk04'), # 0
        Offset64('unk08'),

        ('I',  'num_strs'),
        Padding(4),
        size = 0x18,
    )

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the table from given FRES."""
        super().readFromFRES(fres, offset, reader)
        self.dumpToDebugLog()
        self.dumpOffsets()

        self.strings = []
        self.fres.file.seek(self._file_offset + self._reader.size)
        for i in range(self.num_strs):
            offs = self.fres.file.tell()
            self.strings.append(self.fres.readStr(offs))
            log.debug('Str 0x%02X: "%s"', i, self.strings[-1])
        return self


    def validate(self):
        super().validate()
        return True
