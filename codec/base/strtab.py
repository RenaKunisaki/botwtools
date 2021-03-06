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
from codec.base.types import Offset, Offset64, StrOffs, Padding
from structreader import StructReader, BinaryObject, readStringWithLength

class StringTable(BinaryObject):
    """String table."""
    _magic = b'_STR'
    _reader = StructReader(
        ('4s', 'magic'),    Padding(4),
        ('I',  'size'),     Padding(4),
        ('I',  'num_strs'), Padding(4),
        size = 0x18,
    )

    def _unpackFromData(self, data):
        super()._unpackFromData(data)

        self.strings = []
        self._file.seek(self._file_offset + self._reader.size)
        for i in range(self.num_strs):
            offs = self._file.tell()
            offs += (offs & 1) # pad to u16
            self.strings.append(readStringWithLength(self._file, '<H', offs))
            #log.debug('Str 0x%04X: "%s"', i, self.strings[-1])
        return self


    def validate(self):
        super().validate()
        return True
