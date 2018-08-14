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

class NameTableHeader(BinaryObject):
    """SARC file SFAT filename table header."""
    _reader = StructReader(
        ('4s', 'magic'), # 'SFNT'
        ('H',  'header_len'), # always 8
        ('H',  'reserved06'),
    )

    def validate(self):
        assert self.magic == b'SFNT', "Not an SFNT object"
        if self.reserved06 != 8:
            log.warn("SFNT reserved06 is %d, should be 8",
                self.reserved06)
        return True
