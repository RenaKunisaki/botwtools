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
from codec.base.types import Offset, Offset64, StrOffs
from structreader import StructReader, BinaryObject

class FresObject(BinaryObject):
    def __init__(self):
        self.name = None

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the object from given FRES."""
        super().readFromFile(fres.file, offset, reader)
        self.fres = fres

        # read strings.
        for name, field in self._reader.fields.items():
            typ = field['type']
            if isinstance(typ, StrOffs):
                offs = getattr(self, name)
                if offs > 0:
                    data = typ.readStr(self.fres.file, offs)
                else:
                    data = None
                setattr(self, name+'_offset', offs)
                setattr(self, name, data)


    def _dumpOffset(self, name, offs):
        try:
            data = []
            text = []
            for i in range(8):
                data.append(self._file.read('I', offs + (i*4)))
                for j in range(4):
                    c = self._file.read('B', offs + (i*4) + j)
                    if c < 0x20 or c > 0x7E: c = '.'
                    else: c = chr(c)
                    text.append(c)
            data = ' '.join(map(lambda v: '%08X' % v, data))
            text = ''.join(text)
        except struct.error:
            data = "<out of range>"
            text = ''
        log.debug("%16s %06X => %s '%s'", name, offs, data, text)


    def dumpOffsets(self):
        """Dump the values found at each field treated as an offset."""
        for name, field in self._reader.fields.items():
            val = getattr(self, name)
            if type(val) is int and val >= 0xD0 and val < 0xFFFFFF:
                self._dumpOffset(name, val)
                if self.fres.rlt:
                    self._dumpOffset(" reloc", val+self.fres.rlt.data_start)
