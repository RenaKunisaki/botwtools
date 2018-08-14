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

        StrOffs('name', None),
        ('I',  'unk14'),      # 00D00000 u16 full header size?
        Offset('rlt_offset'),
        ('I',  'file_size'),  # size of this file

        StrOffs('name2'),
        Padding(4),
        Offset('fmdl_offset'),
        Padding(4),

        Offset('unk30'), # 00000448 points to: 0, #objs, -1, 1
        ('I',  'unk34'), # 00000000
        ('I',  'unk38'), # 00000000
        ('I',  'unk3C'), # 00000000

        ('I',  'unk40'), # 00000000
        ('I',  'unk44'), # 00000000
        Offset('fmaa_offset'),
        Padding(4),

        Offset('unk50'), # 000004C0 points to: 0, 1, -1, 1
        ('I',  'unk54'), # 00000000
        ('I',  'unk58'), # 00000000
        ('I',  'unk5C'), # 00000000

        ('I',  'unk60'), # 00000000
        ('I',  'unk64'), # 00000000
        ('I',  'unk68'), # 00000000
        ('I',  'unk6C'), # 00000000

        ('I',  'unk70'), # 00000000
        ('I',  'unk74'), # 00000000
        ('I',  'unk78'), # 00000000
        ('I',  'unk7C'), # 00000000

        ('I',  'unk80'), # 00000000
        ('I',  'unk84'), # 00000000
        ('I',  'unk88'), # 00021000
        ('I',  'unk8C'), # 00000000

        ('I',  'unk90'), # 00000418
        ('I',  'unk94'), # 00000000
        ('I',  'unk98'), # 00000438
        ('I',  'unk9C'), # 00000000

        ('I',  'unkA0'), # 000004E8
        ('I',  'unkA4'), # 00000000
        ('I',  'unkA8'), # 00000000
        ('I',  'unkAC'), # 00000000

        ('I',  'unkB0'), # 0001A224 just before name table
        ('I',  'unkB4'), # 00000000
        ('I',  'unkB8'), # 00003570 size of string table?
        ('I',  'num_objects'), # 00000006 number of models?

        ('I',  'unkC0'), # 00000001
        ('I',  'unkC4'), # 00000000
        ('I',  'unkC8'), # 00000001
        ('I',  'unkCC'), # 00000000

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
