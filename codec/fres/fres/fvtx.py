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
from .fresobject import FresObject
from codec.base.types import Offset, Offset64, StrOffs, Padding
from codec.base.dict  import Dict
from structreader import StructReader, BinaryObject
from .attribute import Attribute
from .buffer import Buffer
from .vertex import Vertex
from .types import attrFmts

class FVTX(FresObject):
    """A FVTX in an FMDL."""
    # vertex buffer object attributes
    _magic = b'FVTX'
    _reader = StructReader(
        ('4s', 'magic'),
        ('3I', 'unk04'),
        Offset64('vtx_attrib_array_offs'),
        Offset64('vtx_attrib_dict_offs'),
        Offset64('unk10'),
        Offset64('unk18'),
        Offset64('unk20'),
        Offset64('vtx_bufsize_offs'),
        Offset64('vtx_stridesize_offs'),
        Offset64('vtx_buf_array_offs'),
        Offset('vtx_buf_offs'),
        ('B',  'num_attrs'),
        ('B',  'num_bufs'),
        ('H',  'index'), # Section index: index into FVTX array of this entry.
        ('I',  'num_vtxs'),
        ('I',  'skin_weight_influence'),
        size = 0x60,
    )

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the FVTX from given FRES."""
        super().readFromFRES(fres, offset, reader)

        self.dumpToDebugLog()
        #self.dumpOffsets()

        self._readDicts()
        self._readBuffers()
        self._readAttrs()
        self._readVtxs()

        return self


    def _readDicts(self):
        self.vtx_attrib_dict = Dict().readFromFile(self.fres.file,
            self.vtx_attrib_dict_offs)
        log.debug("FVTX attrib dict:")
        self.vtx_attrib_dict.dumpToDebugLog()


    def _readBuffers(self):
        dataOffs = self.fres.rlt.data_start + self.vtx_buf_offs
        self.buffers = []
        file = self.fres.file
        for i in range(self.num_bufs):
            n      = i*0x10
            size   = file.read('I', self.vtx_bufsize_offs+n)
            stride = file.read('I', self.vtx_stridesize_offs+n)
            buf    = Buffer(file, size, stride, dataOffs)
            self.buffers.append(buf)
            dataOffs += buf.size


    def _readAttrs(self):
        self.attrs = []
        self.attrsByName = {}
        for i in range(self.num_attrs):
            attr = Attribute().readFromFRES(self.fres,
                self.vtx_attrib_array_offs +
                (i * Attribute._reader.size))
            #log.debug("Attr: %s", attr)
            attr.fvtx = self
            self.attrs.append(attr)
            self.attrsByName[attr.name] = attr


    def _readVtxs(self):
        self.vtxs  = []
        for i in range(self.num_vtxs):
            vtx = Vertex()
            for attr in self.attrs:
                buf  = self.buffers[attr.buf_idx]
                offs = attr.buf_offs + (i * buf.stride)
                fmt  = attrFmts.get(attr.format, None)
                if fmt is None:
                    log.error("Unsupported attribute data type: 0x%04X",
                        attr.format)
                    break

                func = None
                if type(fmt) is dict:
                    func = fmt.get('func', None)
                    fmt  = fmt['fmt']
                data = struct.unpack_from(fmt, buf.data, offs)
                if func: data = func(data)
                #log.debug("vtx %d attr %s = %s", i, attr.name, data)
                vtx.setAttr(attr, data)

            self.vtxs.append(vtx)


    def validate(self):
        super().validate()
        return True
