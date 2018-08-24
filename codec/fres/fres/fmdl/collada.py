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
import myxml
from ..types import attrFmts

attr_types = {
    # attribute name => {
    #   name: displayed name
    #   semantic: the access semantic as specified by COLLADA
    #   params: list of parameter names
    # }
    #
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
        'name':    "Normal",
        'semantic':'NORMAL',
        'params': ('X', 'Y', 'Z'),
    },
    '_p0': {
        'name':    "Position",
        'semantic':'POSITION',
        'params': ('X', 'Y', 'Z'),
    },
    '_u0': {
        'name':    "UV Map",
        'semantic':'TEXCOORD',
        'params': ('S', 'T'),
        'set':    0,
    },
    '_u1': {
        'name':    "Secondary UV Map",
        'semantic':'TEXCOORD',
        'params': ('S', 'T'),
        'set':    1,
    },
    '_w0': {
        'name':    "Weight",
        'semantic':'WEIGHT',
        'params': ('W',),
    },
}

class ColladaWriter:
    """Takes objects found in an FRES and creates
    a COLLADA file from them.
    """
    def __init__(self):
        self.effects     = []
        self.materials   = []
        self.geometries  = []
        self.images      = []
        self.scenes      = []
        self.meshes      = []
        self.vtxs        = []
        self.textures    = []
        self.scene_nodes = []
        self.fmats       = []
        self.fvtxs       = []


    def addScene(self, name="Untitled"):
        scene = myxml.Element('visual_scene',
            *self.scene_nodes,
            id   = 'scene%d' % len(self.scenes),
            name = name,
        )
        self.scenes.append(scene)


    def addFVTX(self, fvtx, name=None):
        """Add an FVTX to the file."""
        fvid = 'fvtx%d' % len(self.fvtxs)
        self.fvtxs.append(fvtx)


    def addFSHP(self, fshp):
        """Add an FSHP to the file."""
        for i, lod in enumerate(fshp.lods):
            name = '%s.%d' % (fshp.name, i)
            self._makePlistForLod(fshp, lod, name, i)


    def addFMAT(self, fmat):
        """Add an FMAT to the file."""
        matid = 'material%d' % len(self.materials)
        self.fmats.append(fmat)

        # add element to materials
        elem = myxml.Element('material', id=matid, name=fmat.name)
        self.materials.append(elem)

        # create effect
        for tex in fmat.textures:
            effid = 'effect%d' % len(self.effects)
            elem.Child('instance_effect', url='#'+effid)
            eff = self._makeMatTexEntry(fmat, tex, effid)
            self.effects.append(eff)


    def _makeMatTexEntry(self, fmat, tex, effid):
        """Make nodes for a material's texture."""
        texid = 'texture%d' % len(self.textures)
        srfid = 'surface%d' % len(self.textures)
        smpid = 'sampler%d' % len(self.textures)
        elem  = myxml.Element('effect', id=effid)
        prof  = elem.Child('profile_COMMON')

        # param to define the surface
        surf = prof.Child('newparam', sid=srfid) \
            .Child('surface', type='2D') \
            .Child('init_from')
        surf.text = texid

        # param to sample the surface
        samp = prof.Child('newparam', sid=smpid) \
            .Child('sampler2D') \
            .Child('source')
        samp.text = srfid

        # technique to use that sampler
        prof.Child('technique', sid='COMMON') \
            .Child('lambert') \
            .Child('diffuse') \
            .Child('texture', texture=smpid, texcoord="geometry0_lod0_src4") # XXX

        # add the texture to the images
        img = myxml.Element('image', id=texid)
        self.images.append(img)
        init = img.Child('init_from')
        init.text = 'textures/' + tex['name'] + '.png'

        self.textures.append(tex)
        return elem



    def _makePlistForLod(self, fshp, lod, name, idx):
        """Build plist element for LOD model. Called by addFSHP."""
        # generate IDs
        gid  = 'geometry%d' % len(self.geometries)
        vid  = 'vertices%d' % len(self.geometries)
        if name is None: name = gid

        matid = 'material%d' % fshp.fmat_idx
        mat   = self.fmats[fshp.fmat_idx]

        # create geometry and mesh
        geom = myxml.Element('geometry', id=gid, name=name)
        self.geometries.append(geom)
        mesh = geom.Child('mesh')
        self.meshes.append(mesh)

        # mesh -> vertices -> input, mesh -> source, mesh -> triangles
        vtxs = myxml.Element('vertices', id=vid)
        self.vtxs.append(vtxs)
        tris = myxml.Element(self._getPrimFmt(lod),
            count=len(lod.faces), material=mat.name)
        log.debug("LOD %s prim_fmt=%s", name, self._getPrimFmt(lod))
        input_cnt = {}
        fvtx = self.fvtxs[0]
        max_offs = 0
        for j, attr in enumerate(fvtx.attrs):
            if attr.name in attr_types:
                srcid = '%s_lod%d_src%d' % (gid, idx, j)
                typ   = attr_types[attr.name]

                # get the buffer and format
                # idx = which data buffer to read
                # offset = where in the index buffer to read (in bytes)
                # atr fmt  offs   idx
                # _p0 1505  0      0
                # _n0 0E02  0      1
                # _t0 0B02  4      1
                # _b0 0B02  0      2
                # _u0 1201  8      1
                # _u1 1201 12      1
                # so the index buffer is (p0+n0+b0, t0, u0, u1)
                # ie the first index specifies p0, n0, and b0
                # but they each read from a different buffer
                # but this seems to not make sense with the indices given:
                # 0 1 2  1 3 2  4 5 6  5 7 6
                # these are clearly groups of 3, not 4...
                # so is there another index buffer?
                # perhaps it's the fvtx.index attribute...

                buf  = fvtx.buffers[attr.buf_idx]
                fmt  = attrFmts.get(attr.format)
                func = None
                if type(fmt) is dict:
                    func = fmt.get('func', None)
                    fmt  = fmt['fmt']

                log.debug("model attr %s type 0x%04X", attr.name, attr.format)

                # get the data from the buffer
                data = []
                sz   = struct.calcsize(fmt)
                for k in range(attr.buf_offs, int(buf.size / sz)):
                    d = struct.unpack_from(fmt, buf.data, k*sz)
                    if func: d = func(d)
                    for item in d: data.append(item)

                # stupid
                if attr.name == '_p0':
                    data = self._fixPositionsForBlender(data)
                elif attr.name in ('_u0', '_u1'):
                    data = self._fixTexcoordsForBlender(data)

                src = mesh.Child('source', id=srcid, name=attr.name)
                src.append(self._makeArrayForAttribute(attr, data, srcid))
                src.append(self._makeAccessorForAttribute(attr, data, srcid))

                #The first index in a <p> element refers to all inputs with
                #an offset attribute value of 0. The second index refers to
                #all inputs with an offset of 1. There is an index value for
                #each unique input offset attribute value. Each vertex of
                #the primitive is assembled using the value(s) read from
                #indexed inputs. After each input is sampled, producing a
                #primitive vertex, the next index in the <p> element again
                #refers to the inputs with offset of 0

                offset = int(attr.buf_offs / sz)
                semantic = typ['semantic']
                if semantic == 'POSITION':
                    vtxs.Child('input',
                        semantic = typ['semantic'],
                        source   = '#'+srcid,
                    )
                    semantic = 'VERTEX'

                if semantic not in input_cnt: input_cnt[semantic] = 0
                input = tris.Child('input',
                    offset   = offset, #len(input_cnt) - 1,
                    semantic = semantic,
                    source   = '#'+srcid,
                )
                if 'set' in typ:
                    input.set('set', typ['set'])
                input_cnt[semantic] += 1
                max_offs = max(max_offs, offset)
        mesh.append(vtxs)
        mesh.append(tris)

        # triangles -> vcount, triangles -> p
        sizes  = []
        faces  = []
        offset = len(input_cnt)
        log.debug("idxs: %s", lod.idxs)
        for face in lod.idxs:
            faces.append(face)

        #vcount = tris.Child('vcount')
        #vcount.text = ' '.join(map(str, sizes))
        p = tris.Child('p')
        p.text = ' '.join(map(str, faces))


        # node -> instance_geometry
        node = myxml.Element('node', name=name, type='NODE',
            id = 'node%d' % len(self.scene_nodes),
        )
        inst = node.Child('instance_geometry', url='#'+gid)
        inst.Child('bind_material') \
            .Child('technique_common') \
            .Child('instance_material',
                symbol=mat.name, target='#'+matid) \
            .Child('bind_vertex_input', semantic="_u0",
                input_semantic="TEXCOORD", input_set=0)

        self.scene_nodes.append(node)


    def _getPrimFmt(self, lod):
        # <lines>, <linestrips>, <polygons>, <polylists>, <triangles>, <trifans> and <tristrips>
        if lod.prim_fmt in ('line_strip', 'line_loop'):
            #elem = 'lines'
            return 'triangles' # XXX
        elif lod.prim_fmt == 'triangles':
            return 'triangles'
        else:
            log.error("Unsupported prim fmt %s", lod.prim_fmt)
            return None


    def _serializeAttribute(self, attr, fvtx):
        """Given an attribute in an FVTX, create the elements for it."""
        # first, a source
        if attr.name in attr_types:
            name = attr_types[attr.name]['name']
        else:
            name = attr.name
        src = myxml.Element('source', id=attr.name, name=name)

        # get the buffer and format
        buf  = fvtx.buffers[attr.buf_idx]
        fmt  = attrFmts.get(attr.format)
        func = None
        if type(fmt) is dict:
            func = fmt.get('func', None)
            fmt  = fmt['fmt']

        # get the data from the buffer
        data = []
        sz   = struct.calcsize(fmt)
        for i in range(int(buf.size / sz)):
            d = struct.unpack_from(fmt, buf.data, i*sz)
            if func: d = func(d)
            for item in d: data.append(item)

        # stupid
        if attr.name == '_p0':
            data = self._fixPositionsForBlender(data)

        # make elements for the data
        arr = self._makeArrayForAttribute   (attr, data)
        acc = self._makeAccessorForAttribute(attr, data)
        if arr: src.append(arr)
        if acc: src.append(acc)

        # create the input element for this source
        if attr.name in attr_types:
            input = myxml.Element('input',
                semantic = attr_types[attr.name]['semantic'],
                source = '#'+attr.name,
            )
        else: # we don't know what to use this attribute for
            input = None

        return src, input


    def _fixPositionsForBlender(self, data):
        """Take `data` and return a copy with every 4th element removed.
        This is necessary to remove the W position from vertices
        because Blender refuses to import a Collada file whose
        vertices don't have a stride of 3.
        """
        res = []
        for i in range(0, len(data), 4):
            res += data[i:i+3] # skip every 4th item
        return res

    def _fixTexcoordsForBlender(self, data):
        res = []
        for i in range(0, len(data), 2):
            res += (data[i], data[i+1])
        return res


    def _makeArrayForAttribute(self, attr, data, srcid):
        """Make the array element for an attribute's data."""
        typ = attrFmts[attr.format]
        if typ['collada_type'] == 'int':
            dmin, dmax = typ['min'], typ['max']
            data = list(map(lambda d: d/(dmax-dmin)+dmin, data))

        arr = myxml.Element('float_array',
            id = '%s_%s' % (srcid, attr.name),
            count = len(data),
        )
        # apparently Blender doesn't like these
        #if typ['collada_type'] == 'int':
        #    arr.set('mininclusive', typ['min'])
        #    arr.set('maxinclusive', typ['max'])
        arr.text = ' '.join(map(str, data))
        return arr


    def _makeAccessorForAttribute(self, attr, data, srcid):
        """Make the accessor/technique elements for an attribute."""
        # XXX support more types of accessor/technique
        if attr.name not in attr_types: return None
        typ    = attrFmts[attr.format]
        offs   = attr.buf_offs #* buf.stride
        tech   = myxml.Element('technique_common')
        params = attr_types[attr.name]['params']
        acc    = tech.Child('accessor',
            count  = len(data)*len(params), # XXX what is this
            offset = offs,
            stride = len(params),
            source = '#'+srcid,
        )
        for p in params:
            acc.Child('param', name=p,
                #type=typ['collada_type']
                type='float'
                )
        return tech


    def toXML(self):
        """Generate XML document for this file."""
        document = myxml.Document('COLLADA',
            myxml.Element('asset', myxml.Element('up_axis', 'Y_UP')),
            #myxml.Element('library_cameras',       *self.cameras),
            #myxml.Element('library_lights',        *self.lights),
            myxml.Element('library_effects',       *self.effects),
            myxml.Element('library_images',        *self.images),
            myxml.Element('library_materials',     *self.materials),
            myxml.Element('library_geometries',    *self.geometries),
            myxml.Element('library_visual_scenes', *self.scenes),
            xmlns="http://www.collada.org/2005/11/COLLADASchema",
            version="1.4.1",
        )
        root = document.root
        for scene in self.scenes:
            root.Child('scene').Child(
                'instance_visual_scene', url='#'+scene.get('id'))
        return document
