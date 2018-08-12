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
from structreader import StructReader, BinaryObject, readStringWithLength
from .attribute import Attribute
from .buffer import Buffer
from .vertex import Vertex

class FVTX(BinaryObject):
    """A FVTX in an FMDL."""
    # vertex buffer object attributes
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

    def unpack10bit(val):
        # XXX sign bit
        if type(val) in (list, tuple):
            val = val[0] # grumble grumble struct is butts
        v0 = ( val        & 0x3FF) / 511
        v1 = ((val >> 10) & 0x3FF) / 511
        v2 = ((val >> 20) & 0x3FF) / 511
        return v0, v1, v2

    attrFmts = {
        0x0201: 'B',
        0x0901: '2B',
        0x0B01: '4B',
        0x1201: '2H',
        0x1501: '2h',
        0x1701: '2i',
        0x1801: '3i',
        0x0B02: '4B',
        0x0E02: {'fmt':'I', 'func':unpack10bit},
        0x1202: '2h',
        0x0203: 'B',
        0x0903: '2B',
        0x0B03: '4B',
        0x1205: '2e',
        0x1505: '4e',
        0x1705: '2f',
        0x1805: '3f',
    }

    def readFromFile(self, file, offset=None, reader=None):
        """Read the FVTX from given file."""
        log.debug("Reading FVTX from 0x%08X", offset)
        super().readFromFile(file, offset, reader)

        self.attrs = []
        self.vtxs  = []
        self.dumpToDebugLog()
        self.dumpOffsets()

        return self


    def _readBuffers(self, file, rlt):
        dataOffs = rlt.data_start + self.vtx_buf_offs
        self.buffers = []
        for i in range(self.num_bufs):
            n = i*0x10
            size   = file.read('I', self.vtx_bufsize_offs+n)
            stride = file.read('I', self.vtx_stridesize_offs+n)
            buf = Buffer(file, size, stride, dataOffs)
            self.buffers.append(buf)
            dataOffs += buf.size


    def _readAttrs(self, file):
        for i in range(self.num_attrs):
            attr = Attribute().readFromFile(file,
                self.vtx_attrib_array_offs +
                (i * Attribute._reader._dataSize))
            log.debug("Attr: %s", attr)
            self.attrs.append(attr)


    def _readVtxs(self, file):
        for i in range(self.num_vtxs):
            vtx = Vertex()
            for attr in self.attrs:
                buf  = self.buffers[attr.buf_idx]
                offs = attr.buf_offs * buf.stride
                fmt  = self.attrFmts.get(attr.format, None)
                if fmt is None:
                    log.error("Unsupported attribute data type: 0x%04X",
                        attr.format)
                    break

                func = None
                if type(fmt) is dict:
                    func = fmt['func']
                    fmt  = fmt['fmt']
                data = struct.unpack_from(fmt, buf.data, offs)
                if func: data = func(data)
                vtx.setAttr(attr, data)

            self.vtxs.append(vtx)


    def validate(self):
        assert self.magic == b'FVTX', "Not an FVTX"
        return True
