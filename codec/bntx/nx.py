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
#from .fresobject import FresObject
from codec.base.types import Offset, Offset64, StrOffs, Padding
from structreader import StructReader, BinaryObject
from codec.base.strtab import StringTable

class NX(BinaryObject):
    """A 'NX' texture in a BNTX."""
    _magic = b'NX  '
    _reader = StructReader(
        ('4s',   'magic'),
        ('I',    'num_textures'),
        Offset64('info_ptrs_offset'),
        Offset64('data_blk_offset'),
        Offset64('dict_offset'),
        ('I',    'str_dict_len'),
    )
