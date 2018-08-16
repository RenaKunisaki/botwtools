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
from .fresobject import FresObject
from codec.base.types import Offset, Offset64, StrOffs, Padding
from structreader import StructReader, BinaryObject
from .fmat import FMAT
from .fshp import FSHP
from .fskl import FSKL
from .fvtx import FVTX

attr_types = {
    # [TEX}BINORMAL, CONTINUITY, IMAGE, INPUT, WEIGHT,
    # INTERPOLATION, INV_BIND_MATRIX, UV, VERTEX, JOINT,
    # LINEAR_STEPS, NORMAL, OUTPUT, TEXCOORD, POSITION,
    # MORPH_{TARGET, WEIGHT}, {TEX}TANGENT,
    # {IN, OUT}_TANGENT
    #'_i0': {
    #    'semantic':'COLOR',
    #    'params': ('R', 'G', 'B', 'A'),
    #},
    '_n0': {
        'semantic':'NORMAL',
        'params': ('X', 'Y', 'Z'),
    },
    '_p0': {
        'semantic':'POSITION',
        'params': ('X', 'Y', 'Z'),
    },
    '_u0': {
        'semantic':'UV',
        'params': ('U', 'V'),
    },
    '_u1': {
        'semantic':'UV',
        'params': ('U', 'V'),
    },
    '_w0': {
        'semantic':'WEIGHT',
        'params': ('W',),
    },
}


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
        Offset64('fshp_dict'),
        Offset64('fmat_offset'),
        Offset64('fmat_dict'),
        Offset64('udata_offset'),
        Offset64('unk60'),
        Offset64('unk68'),

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


    def getFiles(self):
        return ({'name':self.name, 'data':self.serialize()},)


    def serialize(self):
        """Export model to COLLADA file."""
        # initial document structure
        document = myxml.Document('COLLADA',
            myxml.Element('library_cameras'),
            myxml.Element('library_lights'),
            myxml.Element('library_materials'),
            myxml.Element('library_effects'),
            xmlns="http://www.collada.org/2005/11/COLLADASchema",
            version="1.4.1",
        )
        root = document.root

        geoms = root.Child('library_geometries')
        gids  = []
        for geom in self.fvtxs:
            gids.append('geometry%d' % id(geom))
            geoms.append(self._serializeGeometry(geom))

        # make a scene
        scenes = root.Child('library_visual_scenes')
        scene  = scenes.Child('visual_scene',
            id   = 'scene0',
            name = 'untitled',
        )
        for i, gid in enumerate(gids):
            node = scene.Child('node',
                id   = 'node_'+gid,
                name = self.fshps[i].name,
            )
            node.Child('instance_geometry', url='#'+gid)
        root.Child('scene').Child('instance_visual_scene', url='#scene0')

        return document.tostring(pretty_print=True)


    def _serializeGeometry(self, geom):
        gid  = 'geometry%d' % id(geom)
        elem = myxml.Element('geometry',
            id = gid,
            name = self.name,
        )

        vid  = 'vertices%d' % id(geom)
        mesh = elem.Child('mesh')
        vtxs = mesh.Child('vertices', id=vid)
        for attr in geom.attrs:
            src, input = self._serializeAttribute(attr, geom)
            if src: mesh.append(src)
            if input: vtxs.append(input)

        # XXX why do this here?
        for fshp in self.fshps:
            for lod in fshp.lods:
                plist = self._exportLod(lod, '#'+vid)
                if plist: mesh.append(plist)

        return elem


    def _serializeAttribute(self, attr, geom):
        elem = myxml.Element('source', id=attr.name, name=attr.name)
        buf  = geom.buffers[attr.buf_idx]
        fmt  = geom.attrFmts.get(attr.format)
        func = None
        if type(fmt) is dict:
            func = fmt['func']
            fmt  = fmt['fmt']
        data = []
        sz   = struct.calcsize(fmt)
        for i in range(int(buf.size / sz)):
            d = struct.unpack_from(fmt, buf.data, i*sz)
            if func: d = func(d)
            for item in d: data.append(item)

        # stupid
        if attr.name == '_p0':
            data = self._fixBufferForBlender(data)

        arr = self._makeArrayForAttribute   (attr, data)
        acc = self._makeAccessorForAttribute(attr, data)
        if arr: elem.append(arr)
        if acc: elem.append(acc)

        if attr.name in attr_types:
            input = myxml.Element('input',
                semantic = attr_types[attr.name]['semantic'],
                source = '#'+attr.name,
            )
        else:
            input = None

        return elem, input


    def _fixBufferForBlender(self, data):
        """Take `data` and return a copy with every 4th element removed.
        This is necessary to remove the W position from vertices
        because Blender refuses to import a Collada file whose
        vertices don't have a stride of 3.
        """
        res = []
        for i in range(0, len(data), 4):
            res += data[i:i+3] # skip every 4th item
        return res


    def _makeArrayForAttribute(self, attr, data):
        # XXX use attr.format instead of always float
        arr = myxml.Element('float_array',
            id = 'array%d' % id(attr),
            count = len(data),
        )
        arr.text = ' '.join(map(str, data))
        return arr


    def _makeAccessorForAttribute(self, attr, data):
        # XXX support more types of accessor/technique
        if attr.name not in attr_types: return None
        offs = attr.buf_offs #* buf.stride
        tech = myxml.Element('technique_common')
        params = attr_types[attr.name]['params']
        acc  = tech.Child('accessor',
            count  = len(data)*len(params), # XXX what is this
            offset = offs,
            stride = len(params),
            source = '#array%d' % id(attr),
        )
        for p in params:
            acc.Child('param', name=p, type='float')
        return tech


    def _exportLod(self, lod, vtxs_id):
        # <lines>, <linestrips>, <polygons>, <polylists>, <triangles>, <trifans> and <tristrips>
        if lod.prim_fmt in ('line_strip', 'line_loop'):
            #elem = 'lines'
            elem = 'triangles'
        elif lod.prim_fmt == 'triangles':
            elem = 'triangles'
        else:
            log.error("Unsupported prim fmt %s", lod.prim_fmt)
            return None

        plist = myxml.Element(elem, count=len(lod.faces))
        inp_vtx = plist.Child('input',
            offset = '0',
            semantic = 'VERTEX',
            source = vtxs_id,
        )

        sizes = []
        faces = []
        for face in lod.faces:
            sizes.append(len(face))
            faces += face

        vcount = plist.Child('vcount')
        vcount.text = ' '.join(map(str, sizes))
        p = plist.Child('p')
        p.text = ' '.join(map(str, faces))

        return plist
