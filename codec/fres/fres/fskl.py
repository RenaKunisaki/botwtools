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

import logging; log = logging.getLogger()
from structreader import StructReader, BinaryObject
from .bone import Bone

class FSKL(BinaryObject):
    """FSKL object header."""
    # offsets in this struct are relative to the beginning of
    # the FRES file.
    # I'm assuming they're 64-bit.
    _reader = StructReader(
        ('4s', 'magic'), # 'FSKL'
        ('I',  'size'),
        ('I',  'size2'),
        ('I',  'unk0C'), # always 0

        ('Q',  'unk10'), # 0x730
        ('Q',  'unk18'), # 0x6E0

        ('Q',  'unk20'), # 0x730
        ('Q',  'unk28'), # 0x730

        ('Q',  'unk30'), # 0
        ('I',  'unk38'), # 0x1100
        ('H',  'num_bones'),
        ('H',  'unk3E'),

        ('Q',  'unk40'), # 0
    )

    def readFromFile(self, file, offset=None, reader=None):
        """Read the archive from given file."""
        super().readFromFile(file, offset, reader)
        log.debug("FSKL size: 0x%08X (0x%08X)", self.size, self.size2)
        for name, field in self._reader.fields.items():
            val = getattr(self, name)
            if type(val) is int:
                log.debug("FSKL %8s = 0x%08X", name, val)
            else:
                log.debug("FSKL %8s = %s", name, val)

        offs = file.tell()
        for i in range(self.num_bones):
            b = Bone().readFromFile(file, offs)
            offs += Bone._reader._dataSize
        return self


    def validate(self):
        #for field in self._reader.fields.values():
        #    val = getattr(self, field['name'])
        #    if type(val) is int:
        #        log.debug("FMDL[%04X] %16s = 0x%08X", field['offset'],
        #            field['name'], val)
        #    else:
        #        log.debug("FMDL[%04X] %16s = %s", field['offset'],
        #            field['name'], val)

        assert self.magic[0:4] == b'FSKL', "Not a FSKL file"

        return True
