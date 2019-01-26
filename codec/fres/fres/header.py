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
from .rlt import RLT

def isPowerOf2(n):
    return bool(n and not (n&(n-1)))

class Header(FresObject):
    """FRES file header."""
    _magic = (b'FRES', b'FRES    ')

    _reader_wiiu = StructReader( # WiiU header
        ('4s', 'magic'), # 'FRES'
        ('I',  'version'),
        ('H',  'byte_order'), # FFFE=little, FEFF=big
        ('H',  'header_len'), # always 0x10
        ('I',  'file_size'),
        ('I',  'alignment'), # memory alignment to load this file to
        StrOffs('name', None), # offset of file name without extension
        ('I',  'str_tab_len'), # bytes, string table size
        Offset('str_tab_offset'), # string table offset
        ('12I','group_offset'), # offset of each group (0=not present)
        ('12H','group_nfiles'), # num files in each group (excl root)
        ('I',  'user_ptr'), # always 0, changed in memory at runtime
        size = 0x6C,
    )

    _reader_switch = StructReader( # Switch header
        # `name` is the offset of a null-terminated string.
        # `name2` is the offset of a length-prefixed string.
        # Both seem to be the filename without extension.

        ('8s', 'magic'),      # 'FRES    ' (four spaces)
        ('I',  'version'),
        ('H',  'byte_order'), # FFFE=little, FEFF=big
        ('H',  'header_len'), # always 0x0C

        Offset(  'name_offset'),
        Offset(  'alignment'),
        Offset(  'rlt_offset'),
        Offset(  'file_size'),  # size of this file
        StrOffs( 'name2'),
        Offset(  'unk24'), # probably padding

        #Padding(4),
        Offset64('fmdl_offset'),
        Offset64('fmdl_dict_offset'),
        Offset64('fska_offset'),
        Offset64('fska_dict_offset'),
        Offset64('fmaa_offset'),
        Offset64('fmaa_dict_offset'),
        Offset64('fvis_offset'),
        Offset64('fvis_dict_offset'),
        Offset64('fshu_offset'),
        Offset64('fshu_dict_offset'),
        Offset64('fscn_offset'),
        Offset64('fscn_dict_offset'),
        Offset64('buf_mem_pool'),
        Offset64('buf_mem_pool_info'),
        Offset64('embed_offset'),
        Offset64('embed_dict_offset'),
        Offset64('unkA8'),
        Offset64('str_tab_offset'),
        Offset  ('unkB8'), # str tab size?
        ('H',    'fmdl_cnt'),
        ('H',    'fska_cnt'),
        ('H',    'fmaa_cnt'),
        ('H',    'fvis_cnt'),
        ('H',    'fshu_cnt'),
        ('H',    'fscn_cnt'),
        ('H',    'embed_cnt'),
        ('H',    'unkCA'),
        ('H',    'unkCC'),
        ('H',    'unkCE'),

        size = 0xD0,
    )

    def readFromFile(self, file):
        """Read this object from given file."""
        # "FRES    " (with 4 spaces) is Switch format.
        # Without the spaces is WiiU format.
        pos = file.tell()
        magic = file.read(8)
        file.seek(pos, 0)
        if magic == b'FRES    ':
            self.type = 'switch'
            reader = self._reader_switch
        else:
            self.type = 'wiiu'
            reader = self._reader_wiiu
        self._reader = reader
        super().readFromFile(file, reader=reader)

        return self


    def validate(self):
        super().validate()

        assert self.byte_order in (0xFEFF, 0xFFFE), \
            "Invalid byte order mark: 0x%04X" % self.byte_order

        if self.type == 'wiiu':
            if self.header_len != 0x10:
                log.warn("FRES header length is %d, should be 16",
                    self.header_len)

            if self.user_ptr != 0:
                log.warn("FRES user_ptr is 0x%X, should be 0",
                    self.user_ptr)

            if not isPowerOf2(self.alignment):
                log.warn("FRES alignment is 0x%X, should be a power of 2",
                    self.alignment)

        elif self.type == 'switch':
            if self.header_len != 0xC:
                log.warn("FRES header length is %d, should be 12",
                    self.header_len)

        else:
            log.error("FRES unknown type '%s'", self.type)


        return True
