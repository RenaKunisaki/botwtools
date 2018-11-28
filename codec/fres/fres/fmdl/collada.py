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
E = myxml.Element

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
        'name':    "UV Map 0",
        'semantic':'TEXCOORD',
        'params': ('S', 'T'),
    },
    '_u1': {
        'name':    "UV Map 1",
        'semantic':'TEXCOORD',
        'params': ('S', 'T'),
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
        self.controllers = []
        self.effects     = []
        self.fmats       = []
        self.fvtxs       = []
        self.geometries  = []
        self.images      = []
        self.materials   = []
        self.meshes      = []
        self.scene_nodes = []
        self.scenes      = []
        self.textures    = []
        self.vtxs        = []


    def addScene(self, name="Untitled"):
        scene = E('visual_scene',
            *self.scene_nodes,
            id   = 'scene%d' % len(self.scenes),
            name = name,
        )
        self.scenes.append(scene)


    def addFVTX(self, fvtx, name=None):
        """Add an FVTX to the file."""
        #fvid = 'fvtx%d' % len(self.fvtxs)
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
        matElem = E('material', id=matid, name=fmat.name)
        self.materials.append(matElem)

        # create an effect
        effid   = 'effect%d' % len(self.effects)
        effect  = E('effect', id=effid)
        profile = effect.Child('profile_COMMON')
        self.effects.append(effect)
        matElem.Child('instance_effect', url='#'+effid)

        effect.append(self._makeUkingMatNodes(fmat))

        # create a technique and a shader
        tech   = E('technique', sid='common')
        shader = tech.Child('phong')
        shader.Child('emission').Child('color', '0 0 0 1', sid="emission")
        shader.Child('ambient').Child('color', '0 0 0 1', sid="ambient")
        shader.Child('shininess').Child('float', '50', sid="shininess")
        shader.Child('index_of_refraction') \
            .Child('float', '1', sid="index_of_refraction")

        # add the textures to our image list
        for tex in fmat.textures:
            log.debug("fmat %s texture %s", fmat.name, tex['name'])

            texid = tex['name'].replace('.', '_') # XXX ensure valid ID
            img = E('image', id=texid, name=tex['name'])
            self.images.append(img)
            init = img.Child('init_from')
            init.text = 'textures/' + tex['name'] + '.png'
            self.textures.append(tex)

            # create surface from this texture
            srfid = texid + '_surface'
            surf = profile.Child('newparam', sid=srfid) \
                .Child('surface', type='2D') \
                .Child('init_from')
            surf.text = texid

            # create sampler for this surface
            smpid = texid + '_sampler'
            samp = profile.Child('newparam', sid=smpid) \
                .Child('sampler2D') \
                .Child('source')
            samp.text = srfid

            # add texture to the effect
            # XXX there's probably a better way to do this,
            # instead of by name.
            if '_Alb' in tex['name']: # texture
                texcoord = "geometry0_lod0_src4" # XXX
                shader.Child('diffuse') \
                    .Child('texture', texture=smpid, texcoord=texcoord)

            elif '_Nrm' in tex['name']: # normal
                texcoord = "geometry0_lod0_src5" # XXX
                tech.Child('extra') \
                    .Child('technique', profile='FCOLLADA') \
                    .Child('bump') \
                    .Child('texture', texture=smpid, texcoord=texcoord)

            elif '_Spm' in tex['name']: # specular
                texcoord = "geometry0_lod0_src4" # XXX
                shader.Child('specular') \
                    .Child('texture', texture=smpid, texcoord=texcoord)

            else:
                log.warn("Don't know what to do with material %s texture %s", fmat.name, tex['name'])

        profile.append(tech)


    def addFSKL(self, fskl, name=None):
        # https://www.khronos.org/collada/wiki/Skinning
        """Add an FSKL to the file."""
        ctrl_id = 'controller%d' % len(self.controllers)
        controller = E('controller', id=ctrl_id)
        self.controllers.append(controller)

        # XXX which geometry to use here?
        skin   = controller.Child('skin', source='#geometry0')
        skin.Child('bind_shape_matrix',
            "1 0 0 0  0 1 0 0  0 0 1 0  0 0 0 1") # XXX

        # make source for joint names
        arr_id = ctrl_id+'-skin-joints-array'
        cnt = len(fskl.bones)
        src = skin.Child('source', id=ctrl_id+'-skin-joints')
        src.Child('Name_array',
            ' '.join([b.name for b in fskl.bones]),
            id=arr_id, count=cnt)
        src.Child('technique_common') \
            .Child('accessor',
            source='#'+arr_id, count=cnt, stride=1) \
                .Child('param', name='JOINT', type='name')

        # make source for bind_poses
        arr_id = ctrl_id+'-skin-bind_poses-array'
        cnt = len(fskl.inverse_mtxs) * 16
        mtxs = []
        for mtx in fskl.inverse_mtxs:
            for row in mtx:
                mtxs.append(' '.join(map(
                    lambda v: '%5.2f' % v, row)))
            mtxs.append('')
        src = skin.Child('source', id=ctrl_id+'-skin-bind_poses')
        src.Child('float_array', ' '.join(mtxs),
            id=arr_id, count=cnt)
        src.Child('technique_common') \
            .Child('accessor',
            source='#'+arr_id, count=cnt, stride=16) \
                .Child('param', name='TRANSFORM', type='float4x4')

        # make source for skin weights
        arr_id = ctrl_id+'-skin-weights-array'
        cnt = len(fskl.bones)
        src = skin.Child('source', id=ctrl_id+'-skin-weights')
        #src.Child('float_array',
        #    ' '.join([b.name for b in fskl.bones]
        #    id=arr_id, count=cnt)
        src.Child('technique_common') \
            .Child('accessor',
            # XXX count
            source='#geometry0_src_w0', count=42, stride=1) \
                .Child('param', name='WEIGHT', type='float')

        # add the joints
        joints = skin.Child('joints')
        joints.Child('input', semantic='JOINT',
            source='#'+ctrl_id+'-skin-joints')
        joints.Child('input', semantic='INV_BIND_MATRIX',
            source='#'+ctrl_id+'-skin-bind_poses')

        # XXX vertices


    def _makeUkingMatNodes(self, fmat):
        """Make nodes to store the raw material parameters."""
        extra = E('extra')
        tech  = extra.Child('technique', profile='uking')

        rparam = tech.Child('render_params')
        for name, param in fmat.renderParams.items():
            node = rparam.Child(name,
                type=param['type'], count=param['count'])
            for val in param['vals']:
                node.Child('val', val)

        sparam = tech.Child('shader_params')
        for name, param in fmat.shaderParams.items():
            node = sparam.Child(name, type=param['type']['name'],
                #size=param['size'],
                idx0=param['idxs'][0],
                idx1=param['idxs'][1],
                unk00=param['unk00'],
                unk14=param['unk14'],
            )
            node.text = param['type']['outfmt'] % param['data']

        mparam = tech.Child('shader_assign',
            name=fmat.shader_assign.name,
            name2=fmat.shader_assign.name2,
        )
        vattrs = mparam.Child('vtx_attrs',
            count=fmat.shader_assign.num_vtx_attrs)
        for attr in fmat.vtxAttrs:
            vattrs.Child('attr', attr)

        tattrs = mparam.Child('tex_attrs',
            count=fmat.shader_assign.num_tex_attrs)
        for attr in fmat.texAttrs:
            tattrs.Child('attr', attr)

        mattrs = mparam.Child('mat_params',
            count=fmat.shader_assign.num_mat_params)
        for name, param in fmat.mat_params.items():
            mattrs.Child(name, param)

        return extra


    def _makePlistForLod(self, fshp, lod, model_name, idx):
        """Build plist element for LOD model. Called by addFSHP."""
        # generate IDs
        gid  = 'geometry%d' % len(self.geometries)
        vid  = 'vertices%d' % len(self.geometries)
        if model_name is None: model_name = gid

        matid = 'material%d' % fshp.fmat_idx
        mat   = self.fmats[fshp.fmat_idx]

        # create geometry and mesh
        geom = E('geometry', id=gid, name=model_name)
        self.geometries.append(geom)
        mesh = geom.Child('mesh')
        self.meshes.append(mesh)

        # mesh -> vertices -> input, mesh -> source, mesh -> triangles
        vtxs = E('vertices', id=vid)
        vtxs.Child('input', semantic='POSITION', source='#%s_src_p0' % gid)
        self.vtxs.append(vtxs)

        tris = E(self._getPrimFmt(lod),
            count=int(lod.idx_cnt / 3), material=matid) # XXX
        #log.debug("LOD %s prim_fmt=%s", model_name, self._getPrimFmt(lod))

        # make sources for each attribute
        fvtx = self.fvtxs[fshp.fvtx_idx]
        attr_buffers = self._getAttrBuffers(lod, fvtx)
        for name, buf in attr_buffers.items():
            if name in attr_types:
                attr  = fvtx.attrsByName[name]
                typ   = attr_types[name]
                srcid = '%s_src%s' % (gid, name)
                arr   = self._makeArrayForAttribute   (attr, buf, srcid)
                tech  = self._makeAccessorForAttribute(attr, buf, srcid)
                mesh.Child('source', arr, tech, id=srcid, name=name)

                semantic = typ['semantic']
                if semantic == 'POSITION':
                    semantic = 'VERTEX'
                    srcid    = vid
                tris.Child('input',
                    offset   = 0,
                    semantic = semantic,
                    source   = '#'+srcid,
                    set      = name[-1],
                )
        mesh.append(vtxs)
        mesh.append(tris)

        # make p element (index buffer)
        # prefix with \n\t so that editors can fold the data
        # so that we don't have to scroll past it all the time
        tris.Child('p', '\n\t\t\t\t\t\t\t\t\t\t' + (' '.join(map(str, lod.idx_buf))))

        # node -> instance_geometry
        node = E('node', name=model_name, type='NODE',
            id = 'node%d' % len(self.scene_nodes),
        )
        inst = node.Child('instance_geometry', url='#'+gid)
        inst.Child('bind_material') \
            .Child('technique_common') \
            .Child('instance_material',
                symbol=mat.name, target='#'+matid)
            #.Child('bind_vertex_input', semantic="_u0",
            #    input_semantic="TEXCOORD", input_set=0)

        self.scene_nodes.append(node)


    def _getAttrBuffers(self, lod, fvtx):
        """Get attribute data for given LOD.

        lod:  LOD model.
        fvtx: FVTX whose buffers to use.

        Returns a dict of attribute name => [values].
        """
        attr_buffers = {}
        for attr in fvtx.attrs:
            attr_buffers[attr.name] = []

        for submesh in lod.submeshes:
            idxs = submesh['idxs']
            #log.debug("submesh idxs: %s", idxs)
            for idx in range(max(idxs)+1):
                for attr in fvtx.attrs:
                    fmt  = attrFmts.get(attr.format)
                    func = fmt.get('func', None)
                    size = struct.calcsize(fmt['fmt'])
                    buf  = fvtx.buffers[attr.buf_idx]
                    offs = attr.buf_offs + (idx * buf.stride)
                    data = buf.data[offs : offs + size]
                    data = struct.unpack(fmt['fmt'], data)
                    if func: data = func(data)

                    # stupid: strip W coord for Blender;
                    # its importer rejects anything where position's
                    # stride is not 3.
                    if attr.name == '_p0': data = data[0:3]

                    # flip texture Y coord because COLLADA is backward
                    # from what everything else uses
                    elif attr.name in ('_u0', '_u1'):
                        data = (data[0], fmt.get('max', 1) - data[1])

                    if type(data) in (list, tuple):
                        attr_buffers[attr.name] += data
                    else: attr_buffers[attr.name].append(data)

        #for name, buf in attr_buffers.items():
        #    log.debug("%s: %s", name, buf)
        return attr_buffers


    def _getPrimFmt(self, lod):
        """Get primitive element name for LOD."""
        # <lines>, <linestrips>, <polygons>, <polylists>, <triangles>, <trifans> and <tristrips>
        # Blender's importer doesn't support these, so we just use
        # triangles and manually fix up the index buffers.
        if lod.prim_fmt in ('line_strip', 'line_loop'):
            #elem = 'lines'
            return 'triangles' # XXX
        elif lod.prim_fmt == 'triangles':
            return 'triangles'
        else:
            log.error("Unsupported prim fmt %s", lod.prim_fmt)
            return None


    def _makeArrayForAttribute(self, attr, data, srcid):
        """Make the array element for an attribute's data."""
        typ = attrFmts[attr.format]
        if typ['collada_type'] == 'int':
            dmin, dmax = typ['min'], typ['max']
            data = list(map(lambda d: d/(dmax-dmin)+dmin, data))

        arr = E('float_array',
            id = '%s_data' % srcid,
            count = len(data),
        )
        # apparently Blender doesn't like these
        #if typ['collada_type'] == 'int':
        #    arr.set('mininclusive', typ['min'])
        #    arr.set('maxinclusive', typ['max'])
        arr.text = '\n\t\t\t\t\t\t\t\t\t\t' + (' '.join(map(str, data)))
        return arr


    def _makeAccessorForAttribute(self, attr, data, srcid):
        """Make the accessor/technique elements for an attribute."""
        # XXX support more types of accessor/technique
        if attr.name not in attr_types: return None
        typ    = attrFmts[attr.format]
        offs   = attr.buf_offs #* buf.stride
        tech   = E('technique_common')
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
            E('asset',
                E('contributor',
                    E('author', "Nintendo"),
                    E('authoring_tool',
                        "https://github.com/RenaKunisaki/botwtools"
                    ),
                ),
                E('unit', name='meter', meter=1),
                E('up_axis', 'Y_UP'),
            ),
            #E('library_cameras',       *self.cameras),
            #E('library_lights',        *self.lights),
            E('library_effects',       *self.effects),
            E('library_images',        *self.images),
            E('library_materials',     *self.materials),
            E('library_geometries',    *self.geometries),
            E('library_controllers',   *self.controllers),
            E('library_visual_scenes', *self.scenes),
            xmlns="http://www.collada.org/2005/11/COLLADASchema",
            version="1.4.1",
        )
        root = document.root
        for scene in self.scenes:
            root.Child('scene').Child(
                'instance_visual_scene', url='#'+scene.get('id'))
        return document
