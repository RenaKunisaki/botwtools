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
        'semantic':'UV',
        'params': ('U', 'V'),
    },
    '_u1': {
        'name':    "Secondary UV Map",
        'semantic':'UV',
        'params': ('U', 'V'),
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
        self.cameras    = []
        self.lights     = []
        self.effects    = []
        self.materials  = []
        self.geometries = []
        self.scenes     = []
        self.meshes     = []
        self.vtxs       = []
        self.textures   = []
        self.inst_geoms = []
        self.fmats      = []


    def addScene(self):
        scene = myxml.Element('visual_scene',
            *self.inst_geoms,
            id   = 'scene%d' % len(self.scenes),
            name = 'untitled',
        )
        self.scenes.append(scene)


    def addFVTX(self, fvtx, name=None):
        """Add an FVTX to the file."""
        # generate IDs
        gid  = 'geometry%d' % len(self.geometries)
        vid  = 'vertices%d' % len(self.geometries)
        if name is None: name = gid

        # create geometry element
        elem = myxml.Element('geometry', id=gid, name=name)
        self.geometries.append(elem)

        # create geometry -> mesh -> vertices
        mesh = elem.Child('mesh')
        vtxs = mesh.Child('vertices', id=vid)
        self.meshes.append(mesh)
        self.vtxs.append(vtxs)

        # add each attribute to the mesh,
        # and an input for it to the vertices
        for attr in fvtx.attrs:
            src, input = self._serializeAttribute(attr, fvtx)
            if src:   mesh.append(src)
            if input: vtxs.append(input)


    def addFSHP(self, fshp):
        """Add an FSHP to the file."""
        # we need to attach the polylist to a mesh,
        # and it needs to reference a vertices element by ID.
        try: mesh = self.meshes[-1]
        except IndexError:
            log.error("No mesh to attach FSHP to!")
            return

        try: vtxs = self.vtxs[-1]
        except IndexError:
            log.error("No vertex group to attach FSHP to!")
            return

        for lod in fshp.lods:
            # XXX differentiate the resulting geometries somehow.
            # currently they have the same names and everything.
            plist = self._makePlistForLod(fshp, lod, vtxs.get('id'))
            if plist: mesh.append(plist)


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
            .Child('texture', texture=tex['name'], texcoord="_u0")

        self.textures.append(tex)
        return elem



    def _makePlistForLod(self, fshp, lod, vid):
        """Build plist element for LOD model. Called by addFSHP."""
        # <lines>, <linestrips>, <polygons>, <polylists>, <triangles>, <trifans> and <tristrips>
        if lod.prim_fmt in ('line_strip', 'line_loop'):
            #elem = 'lines'
            elem = 'triangles' # XXX
        elif lod.prim_fmt == 'triangles':
            elem = 'triangles'
        else:
            log.error("Unsupported prim fmt %s", lod.prim_fmt)
            return None

        gid = self.geometries[-1].get('id')

        plist = myxml.Element(elem,
            myxml.Element('input',
                offset   = '0',
                semantic = 'VERTEX',
                source   = vid,
            ),
            count=len(lod.faces))

        sizes = []
        faces = []
        for face in lod.faces:
            sizes.append(len(face))
            faces += face

        vcount = plist.Child('vcount')
        vcount.text = ' '.join(map(str, sizes))
        p = plist.Child('p')
        p.text = ' '.join(map(str, faces))

        matid = 'material%d' % fshp.fmat_idx
        mat = self.fmats[fshp.fmat_idx]
        inst = myxml.Element('instance_geometry', url='#'+gid)
        self.inst_geoms.append(inst)
        inst.Child('bind_material') \
            .Child('technique_common') \
            .Child('instance_material',
                symbol=mat.name, target='#'+matid) \
            .Child('bind_vertex_input', semantic="UVSET0",
                input_semantic="TEXCOORD", input_set=0)

        return plist


    def _serializeAttribute(self, attr, fvtx):
        """Given an attribute in an FVTX, create the elements for it."""
        # first, a source
        if attr.name in attr_types:
            name = attr_types[attr.name]['name']
        else:
            name = attr.name
        elem = myxml.Element('source', id=attr.name, name=name)

        # get the buffer and format
        buf  = fvtx.buffers[attr.buf_idx]
        fmt  = fvtx.attrFmts.get(attr.format)
        func = None
        if type(fmt) is dict: # we have a conversion function
            func = fmt['func']
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
            data = self._fixBufferForBlender(data)

        # make elements for the data
        arr = self._makeArrayForAttribute   (attr, data)
        acc = self._makeAccessorForAttribute(attr, data)
        if arr: elem.append(arr)
        if acc: elem.append(acc)

        # create the input element for this source
        if attr.name in attr_types:
            input = myxml.Element('input',
                semantic = attr_types[attr.name]['semantic'],
                source = '#'+attr.name,
            )
        else: # we don't know what to use this attribute for
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
        """Make the array element for an attribute's data."""
        # XXX use attr.format instead of always float
        arr = myxml.Element('float_array',
            id = 'array%d' % id(attr),
            count = len(data),
        )
        arr.text = ' '.join(map(str, data))
        return arr


    def _makeAccessorForAttribute(self, attr, data):
        """Make the accessor/technique elements for an attribute."""
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


    def toXML(self):
        """Generate XML document for this file."""
        document = myxml.Document('COLLADA',
            myxml.Element('library_cameras',       *self.cameras),
            myxml.Element('library_lights',        *self.lights),
            myxml.Element('library_effects',       *self.effects),
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
