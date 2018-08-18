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
import myxml
import struct
from ..fresobject import FresObject
from codec.base.types import Offset, Offset64, StrOffs, Padding
from structreader import StructReader, BinaryObject
from ..fmat import FMAT
from ..fshp import FSHP
from ..fskl import FSKL
from ..fvtx import FVTX
from .collada import ColladaWriter


class FMDL(FresObject):
    """FMDL object header."""
    defaultFileExt = 'dae'
    # offsets in this struct are relative to the beginning of
    # the FRES file.
    # I'm assuming they're 64-bit.
    _magic = b'FMDL'
    _reader = StructReader(
        ('4s', 'magic'),
        ('I',  'size'),
        ('I',  'size2'),
        Padding(4),
        StrOffs('name'),
        Padding(4),
        Offset64('str_tab_end'),
        Offset64('fskl_offset'),

        Offset64('fvtx_offset'),
        Offset64('fshp_offset'),
        Offset64('fshp_dict_offset'),
        Offset64('fmat_offset'),
        Offset64('fmat_dict_offset'),
        Offset64('udata_offset'),
        Offset64('unk60'),
        Offset64('unk68'), # probably dict for unk60

        ('H',  'fvtx_count'),
        ('H',  'fshp_count'),
        ('H',  'fmat_count'),
        ('H',  'udata_count'),
        ('H',  'total_vtxs'),
        Padding(6),
        size = 0x78,
    )

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the archive from given FRES."""
        super().readFromFRES(fres, offset, reader)

        log.debug("FMDL name: '%s'", self.name)
        self.dumpToDebugLog()
        #self.dumpOffsets()

        log.info("FMDL '%s' contains %d skeletons, %d FVTXs, %d FSHPs, %d FMATs, %d udatas, total %d vertices",
            self.name,
            1 if self.fskl_offset > 0 else 0, # can this ever be 0?
            self.fvtx_count, self.fshp_count, self.fmat_count,
            self.udata_count, self.total_vtxs)

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

        #self.fshps = [self.fshps[1]] # XXX DEBUG only keep one model

        return self


    def validate(self):
        super().validate()
        return True


    def toData(self):
        """Export model to COLLADA file."""
        writer = ColladaWriter()

        for i, fvtx in enumerate(self.fvtxs):
            writer.addFVTX(fvtx, name=self.fshps[i].name)
            writer.addFSHP(self.fshps[i]) # XXX this is weird

        for i, fmat in enumerate(self.fmats):
            writer.addFMAT(fmat)

        writer.addScene()
        return writer.toXML().tostring(pretty_print=True)
