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
from structreader import StructReader, BinaryObject, readStringWithLength
from .fmat import FMAT
from .fshp import FSHP
from .fskl import FSKL
from .fvtx import FVTX

class FMDL(BinaryObject):
    """FMDL object header."""
    # offsets in this struct are relative to the beginning of
    # the FRES file.
    # I'm assuming they're 64-bit.
    _reader = StructReader(
        ('4s', 'magic'), # 'FMDL'
        ('I',  'size'),
        ('I',  'size2'),
        ('I',  'unk0C'), # always 0?

        ('Q',  'name_offset'), # name prefixed by u16 len
        ('Q',  'str_tab_end'), # always points to name table?

        ('Q',  'fskl_offset'), # points to FSKL
        ('Q',  'fvtx_offset'), # points to FVTX

        ('Q',  'fshp_offset'), # points to FSHP
        ('Q',  'fshp_dict'), # points to values 0, 1, -1, 1

        ('Q',  'fmat_offset'), # points to FMAT
        ('Q',  'fmat_dict'), # points to 0, 1, -1, 1 (not same as 38)

        ('Q',  'udata_offset'), # same as fskl_offset?
        #('Q',  'unk58'), # always 0?

        # following are just guesses...
        ('2Q', 'unk60'), # always 0?
        ('H',  'fvtx_count'),
        ('H',  'fshp_count'),
        ('H',  'fmat_count'),
        ('H',  'udata_count'),

        ('H',  'total_vtxs'),
    )

    def readFromFile(self, file, offset=None, reader=None):
        """Read the archive from given file."""
        super().readFromFile(file, offset, reader)

        self.name = readStringWithLength(file, '<H', self.name_offset)
        log.debug("FMDL name: '%s'", self.name)
        self.dumpToDebugLog()
        self.dumpOffsets()

        self.skeleton = FSKL().readFromFile(file, self.fskl_offset)

        self.fvtxs = []
        for i in range(self.fvtx_count):
            self.fvtxs.append(FVTX().readFromFile(file,
                self.fvtx_offset + (i*FVTX._reader._dataSize)))

        self.fshps = []
        for i in range(self.fshp_count):
            self.fshps.append(FSHP().readFromFile(file,
                self.fshp_offset + (i*FSHP._reader._dataSize)))

        self.fmats = []
        for i in range(self.fmat_count):
            self.fmats.append(FMAT().readFromFile(file,
                self.fmat_offset + (i*FMAT._reader._dataSize)))

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

        assert self.magic[0:4] == b'FMDL', "Not a FMDL file"

        return True
