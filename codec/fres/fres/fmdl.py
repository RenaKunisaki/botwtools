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
        ('I',  'unk0C'), # padding?
        ('Q',  'name_offset'),
        ('Q',  'str_tab_end'),
        ('Q',  'fskl_offset'),

        ('Q',  'fvtx_offset'),
        ('Q',  'fshp_offset'),
        ('Q',  'fshp_dict'),
        ('Q',  'fmat_offset'),
        ('Q',  'fmat_dict'),
        ('Q',  'udata_offset'),
        ('2Q', 'unk60'),

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

        self.fshps = []
        for i in range(self.fshp_count):
            self.fshps.append(FSHP().readFromFile(file,
                self.fshp_offset + (i*FSHP._reader._dataSize)))

        self.fmats = []
        for i in range(self.fmat_count):
            self.fmats.append(FMAT().readFromFile(file,
                self.fmat_offset + (i*FMAT._reader._dataSize)))

        return self


    def _readVtxs(self, file, rlt):
        for i in range(self.fvtx_count):
            vtx = FVTX().readFromFile(file,
                self.fvtx_offset + (i*FVTX._reader._dataSize))
            vtx._readBuffers(file, rlt)
            vtx._readAttrs(file)
            vtx._readVtxs(file)
            self.fvtxs.append(vtx)


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
