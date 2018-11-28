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
from .fresobject import FresObject
from codec.base.types import Offset, Offset64, StrOffs, Padding

class BoneIdxGroup(FresObject):
    """A bone index group in an FSKL."""
    # offsets in this struct are relative to the beginning of
    # the FRES file.
    # I'm assuming they're 64-bit.
    _reader = StructReader(
        StrOffs('name'),
        ('i',  'unk04'), # always 0 except header
        ('i',  'unk08'), # possibly flags
        ('h',  'unk0A'), # looks like bone idx, but isn't?
        ('h',  'unk0C'), # similar to 0A
    )

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the bone index group from given FRES."""
        super().readFromFRES(fres, offset, reader)

        log.debug("BoneIdxGrp: %3d %3d %3d %3d '%s'",
            self.unk04, self.unk08, self.unk0A, self.unk0C, self.name)
        return self


    def validate(self):
        super().validate()
        return True
