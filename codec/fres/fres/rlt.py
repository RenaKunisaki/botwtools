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

class RLT(FresObject):
    """FRES relocation table."""
    _magic = b'_RLT'
    _reader = StructReader(
        ('4s', 'magic'),
        ('I',  'unk04'), # offset of the RLT?
        ('I',  'unk08'), # 5
        ('I',  'unk0C'), # 0

        ('I',  'unk10'), # 0
        ('I',  'unk14'), # 0
        ('I',  'unk18'), # 0
        ('I',  'unk1C'), # D49E

        ('I',  'unk20'), # 0
        ('I',  'unk24'), # 3D
        ('I',  'unk28'), # 0
        ('I',  'unk2C'), # 0

        Offset('data_start'),
        size = 0x34,
    )


    def validate(self):
        super().validate()
        return True
