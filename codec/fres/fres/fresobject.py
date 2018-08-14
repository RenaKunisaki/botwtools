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
import struct
from .types import Offset, Offset64, StrOffs
from structreader import StructReader, BinaryObject

class FresObject(BinaryObject):
    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the object from given FRES."""
        super().readFromFile(fres.file, offset, reader)
        self.fres = fres

        # read strings.
        for name, field in self._reader.fields.items():
            typ = field['type']
            if isinstance(typ, StrOffs):
                offs = getattr(self, name)
                data = typ.readStr(self.fres.file, offs)
                setattr(self, name+'_offset', offs)
                setattr(self, name, data)


    def _dumpOffset(self, name, offs):
        try:
            data = []
            for i in range(8):
                data.append(self._file.read('I', offs + (i*4)))
            data = ' '.join(map(lambda v: '%08X' % v, data))
        except struct.error:
            data = "<out of range>"
        log.debug("%28s %06X => %s", name, offs, data)


    def dumpOffsets(self):
        """Dump the values found at each field treated as an offset."""
        for name, field in self._reader.fields.items():
            val = getattr(self, name)
            if type(val) is int and val > 0xD0 and val < 0xFFFFFF:
                self._dumpOffset(name, val)
                self._dumpOffset(" reloc", val+self.fres.rlt.data_start)
