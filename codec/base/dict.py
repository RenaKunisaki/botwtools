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
from codec.base.types import Offset, Offset64, StrOffs, Padding
from structreader import StructReader, BinaryObject, readStringWithLength

class Dict(BinaryObject):
    """Dictionary of names."""
    _reader = StructReader(
        ('i',  'unk00'), # always 0?
        ('i',  'numItems'),
        size = 8,
    )
    _itemReader = StructReader(
        ('i', 'search'), # mostly increases, not always by 1
        ('h', 'left'),   # usually -1 for first item
        ('h', 'right'),  # usually  1 for first item
        StrOffs('nameoffs'), Padding(4),
        size = 0x10,
    )

    def _unpackFromData(self, data):
        super()._unpackFromData(data)

        self.items = []
        for i in range(self.numItems+1):
            self._file.seek(self._file_offset + self._reader.size +
                (i*self._itemReader.size))
            item = self._itemReader.unpackFromFile(self._file)
            if item['nameoffs'] == 0: break

            item['name'] = readStringWithLength(self._file,
                '<H', item['nameoffs'])
            self.items.append(item)
        return self


    def dumpToDebugLog(self):
        """Dump to debug log."""
        log.debug("Dict with %d items; unk00 = %d",
            self.numItems, self.unk00)
        for i, item in enumerate(self.items):
            log.debug('%4d: %4d, %4d, %4d, "%s"', i,
                item['search'], item['left'], item['right'],
                item['name'])


    def validate(self):
        super().validate()
        return True
