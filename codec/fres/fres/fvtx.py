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

class FVTX(BinaryObject):
    """A FVTX in an FMDL."""
    _reader = StructReader(
        ('4s', 'magic'),  # 'FVTX'
        ('3I', 'unk04'),
        ('Q',  'vtx_attrib_array_offs'),
        ('Q',  'vtx_attrib_dict_offs'),
        ('Q',  'unk10'),
        ('Q',  'unk18'),
        ('Q',  'unk20'),
        ('Q',  'vtx_bufsize_offs'),
        ('Q',  'vtx_stridesize_offs'),
        ('Q',  'vtx_buf_array_offs'),
        ('I',  'vtx_buf_offs'),
        ('B',  'num_attrs'),
        ('B',  'num_bufs'),
        ('H',  'index'),
        ('I',  'num_vtxs'),
        ('I',  'skin_weight_influence'),
        # size: 0x60
    )

    def readFromFile(self, file, offset=None, reader=None):
        """Read the FVTX from given file."""
        log.debug("Reading FVTX from 0x%08X", offset)
        super().readFromFile(file, offset, reader)

        self.dumpToDebugLog()
        self.dumpOffsets()

        self.vtxs = []
        for i in range(self.num_vtxs):
            vtx = {
                'buf_offs': file.read('H', self.vtx_buf_offs + (2*i)),
            }
            #log.debug("Vtx: %s", vtx)
            self.vtxs.append(vtx)

        return self


    def validate(self):
        assert self.magic == b'FVTX', "Not an FVTX"
        return True
