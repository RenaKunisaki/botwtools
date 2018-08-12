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
from .fmat import FMAT
from .fshp import FSHP
from .fskl import FSKL
from .fvtx import FVTX

class FMDL(BinaryObject):
    """FMDL object header."""
    # offsets in this struct are relative to the beginning of
    # the FRES file.
    # I'm assuming they're 64-bit.
    _magic = b'FMDL'
    _reader = StructReader(
        ('4s', 'magic'),
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

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the archive from given FRES."""
        super().readFromFile(fres.file, offset, reader)
        self.fres = fres

        self.name = fres.readStr(self.name_offset)
        log.debug("FMDL name: '%s'", self.name)
        self.dumpToDebugLog()
        self.dumpOffsets()

        # read skeleton
        self.skeleton = FSKL().readFromFRES(fres, self.fskl_offset)

        # read vertex objects
        self.fvtxs = []
        for i in range(self.fvtx_count):
            vtx = FVTX().readFromFRES(fres,
                self.fvtx_offset + (i*FVTX._reader.size))
            self.fvtxs.append(vtx)

        # read shapes
        self.fshps = []
        for i in range(self.fshp_count):
            self.fshps.append(FSHP().readFromFRES(fres,
                self.fshp_offset + (i*FSHP._reader.size)))

        # read materials
        self.fmats = []
        for i in range(self.fmat_count):
            self.fmats.append(FMAT().readFromFRES(fres,
                self.fmat_offset + (i*FMAT._reader.size)))

        return self


    def validate(self):
        super().validate()
        return True
