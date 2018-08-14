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
from .fresobject import FresObject
from .types import Offset, Offset64, StrOffs, Padding
from structreader import StructReader, BinaryObject

class LODModel(FresObject):
    """A Level-of-Detail Model."""
    _reader = StructReader(
        Offset64('submesh_array_offs'),
        Offset64('unk08'),
        Offset64('unk10'),
        Offset64('idx_buf_offs'),
        ('I',    'face_offs'),# offset into index buffer
        ('I',    'prim_fmt'), # how to draw the faces
        ('I',    'idx_type'), # data type of index buffer entries
        ('I',    'idx_cnt'),  # total number of indices
        ('H',    'visibility_group'),
        ('H',    'submesh_cnt'),
        ('I',    'unk34'),
        size = 0x38,
    )

    primTypes = {
        # id: (min, incr, name)
        0x01: (1, 1, 'points'),
        0x02: (2, 2, 'lines'),
        0x03: (2, 1, 'line_strip'),
        0x04: (3, 3, 'triangles'),
        0x05: (3, 1, 'triangle_fan'),
        0x06: (3, 1, 'triangle_strip'),
        0x0A: (4, 4, 'lines_adjacency'),
        0x0B: (4, 1, 'line_strip_adjacency'),
        0x0C: (6, 1, 'triangles_adjacency'),
        0x0D: (6, 6, 'triangle_strip_adjacency'),
        0x11: (3, 3, 'rects'),
        0x12: (2, 1, 'line_loop'),
        0x13: (4, 4, 'quads'),
        0x14: (4, 2, 'quad_strip'),
        0x82: (2, 2, 'tesselate_lines'),
        0x83: (2, 1, 'tesselate_line_strip'),
        0x84: (3, 3, 'tesselate_triangles'),
        0x86: (3, 1, 'tesselate_triangle_strip'),
        0x93: (4, 4, 'tesselate_quads'),
        0x94: (4, 2, 'tesselate_quad_strip'),
    }
    idxFormats = {
        0x00: '<I', # I/H are backward from gx2Enum.h???
        0x01: '<H',
        0x02: '<I',
        0x04: '>I',
        0x09: '>H',
    }

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the model from given FRES."""
        super().readFromFRES(fres, offset, reader)
        self.dumpToDebugLog()
        self.dumpOffsets()

        #self.groups = []
        ##fres.file.seek(self.face_offs)
        #for i in range(self.visibility_group):
        #    offs, count = fres.read('2I')
        #    log.debug("group %2d: 0x%X, %d", i, offs, count)
        #    self.groups.append((offs, count))

        #self.prim_fmt = 4 # XXX why is this wrong?
        self.prim_fmt_id = self.prim_fmt
        self.prim_min, self.prim_size, self.prim_fmt = \
            self.primTypes[self.prim_fmt]
        self.idx_fmt = self.idxFormats[self.idx_type]
        log.debug("prim fmt: 0x%02X (%s), idx type: 0x%02X (%s) (min=%d inc=%d)",
            self.prim_fmt_id, self.prim_fmt,
            self.idx_type, self.idx_fmt,
            self.prim_min, self.prim_size)

        log.debug("Read %d idxs in fmt %s from 0x%X; idx_buf_offs=0x%X",
            self.idx_cnt, self.idx_fmt, self.face_offs,
            self.idx_buf_offs)
        self.idxs = fres.read(self.idx_fmt,
            pos=self.face_offs, count=self.idx_cnt, use_rlt=True)
        #log.debug("idxs(%d): %s", len(self.idxs), self.idxs)

        self.faces = []
        for i in range(0, self.idx_cnt, self.prim_fmt_id):
            face = []
            for j in range(self.prim_fmt_id):
                face.append(self.idxs[i+j] + self.visibility_group)
            self.faces.append(face)

        return self


    def readFaces(self, buffer):
        #self.faces = []
        #idx = self.face_offs #+ self.prim_min
        #for i in range(0, self.idx_cnt, self.prim_min):
        #    #vtxs = buffer.vtxs[i:i+self.prim_size:]
        #    face = []
        #    for j in range(self.prim_min):
        #        face.append(idx + j)
        #    self.faces.append(face)
        #    idx += self.prim_size

        log.debug("LOD model has %d faces", len(self.faces))
        #for i, face in enumerate(self.faces):
        #    for j, vtx in enumerate(face):
        #        log.debug("%d.%d: %d", i, j, vtx)
        #            #buffer.vtxs[vtx])


    def validate(self):
        super().validate()
        return True
