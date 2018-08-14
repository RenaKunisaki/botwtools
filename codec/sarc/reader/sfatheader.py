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

class SFATHeader(BinaryObject):
    """SARC file SFAT structure header."""
    _reader = StructReader(
        ('4s', 'magic'), # 'SFAT'
        ('H',  'header_len'), # always 0xC
        ('H',  'node_count'),
        ('I',  'hash_key'), # always 0x65
    )

    def validate(self):
        assert self.magic == b'SFAT', "Not a SFAT header"

        if self.header_len != 0xC:
            log.warn("SFAT header length is %d, should be 12",
                self.header_len)
        if self.hash_key != 0x65:
            log.warn("SFAT hash_key is 0x%X, should be 0x65",
                self.hash_key)

        return True
