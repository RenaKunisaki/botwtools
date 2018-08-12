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
import io
import sys
import struct
from lxml import etree as ET
from ..base import ArchiveDecoder, FileReader, UnsupportedFileTypeError, TxtOutput
from ..base.types import Path, BinInput, BinOutput, TxtOutput, fopenMode
from .fres import FRES


class FresDecoder(ArchiveDecoder):
    """Decoder for FRES archive."""
    __codec_name__ = 'FRES'

    def _read(self):
        """Read the input file, upon opening it."""
        self.archive = FRES().readFromFile(self.input)
        log.debug("FRES contains %d models", len(self.archive.models))

    def _iter_objects(self):
        """Iterate over the objects in this file."""
        return iter(self.archive.models)

    def _get_num_objects(self) -> (int, None):
        """Get number of objects in this file.

        Returns None if not known.
        """
        return self.archive.header.num_objects

    def printList(self, dest:TxtOutput=sys.stdout):
        """Print nicely formatted list of this file's objects."""
        print("Models:", self.numObjects)
        for i, obj in enumerate(self.objects):
            print(i, obj.name)
            for bone in obj.skeleton.bones:
                print("  Bone:", bone.name)
            for mat in obj.fmats:
                print(" Material:", mat.name)
            for vtx in obj.fvtxs:
                print(" Vtx:", vtx)
            for shp in obj.fshps:
                print(" Shape:", shp.name)


    def unpack(self):
        """Unpack this file to `self.destPath`."""
        nobj = len(self.archive.models)
        for i, model in enumerate(self.archive.models):
            log.info("[%3d/%3d] Extracting %s...", i+1, nobj, model.name)
            self._extractModel(model)


    def _extractModel(self, model):
        name = model.name + '.dae'
        root = ET.Element('COLLADA')
        root.set('xmlns', "http://www.collada.org/2005/11/COLLADASchema")
        root.set('version', "1.4.1")

        root.append(ET.Element('library_cameras'))
        root.append(ET.Element('library_lights'))
        root.append(ET.Element('library_materials'))
        root.append(ET.Element('library_effects'))

        geoms = ET.Element('library_geometries')
        root.append(geoms)
        geom  = ET.Element('geometry')
        geoms.append(geom)
        geom.set('id', 'geometry%d' % id(model))
        geom.set('name', model.name)

        mesh = ET.Element('mesh')
        geom.append(mesh)
        for fvtx in model.fvtxs:
            for attr in fvtx.attrs:
                src = ET.Element('source')
                mesh.append(src)
                src.set('id', 'src_' + attr.name)
                src.set('name', attr.name)
                #src.set('unk04', '0x%08X' % attr.unk04)
                #src.set('unk0A', '0x%04X' % attr.unk0A)

                buf  = fvtx.buffers[attr.buf_idx]
                offs = attr.buf_offs #* buf.stride
                fmt  = fvtx.attrFmts.get(attr.format)
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
                log.debug("data: %s", data)

                # XXX use attr.format instead of always float
                arr = ET.Element('float_array')
                src.append(arr)
                arr.set('id', 'array%d' % id(attr))
                arr.set('count', str(len(data)))
                arr.text = ' '.join(map(str, data))

                # XXX support more types of accessor/technique
                tech = ET.Element('technique_common')
                src.append(tech)
                acc  = ET.Element('accessor')
                tech.append(acc)
                acc.set('count', str(len(data)*3)) # XXX what is this
                acc.set('offset', str(offs))
                #acc.set('stride', str(buf.stride))
                acc.set('stride', '3')
                acc.set('source', '#array%d' % id(attr))

                for p in ('X', 'Y', 'Z'):
                    param = ET.Element('param')
                    acc.append(param)
                    param.set('name', p)
                    param.set('type', 'float')
            # attrs done...

            vtxs = ET.Element('vertices')
            mesh.append(vtxs)
            vtxs.set('id', 'vertices%d' % id(vtxs))
            input = ET.Element('input')
            vtxs.append(input)
            input.set('semantic', 'POSITION')
            input.set('source', '#src_' + attr.name)

            plist = ET.Element('polylist')
            mesh.append(plist)
            plist.set('count', str(len(fvtx.vtxs))) # XXX probably wrong

            inp_vtx = ET.Element('input')
            plist.append(inp_vtx)
            inp_vtx.set('offset', '0')
            inp_vtx.set('semantic', 'VERTEX')
            inp_vtx.set('source', '#vertices%d' % id(vtxs))

            vcount = ET.Element('vcount')
            plist.append(vcount)
            vcount.text = '4' # XXX

            p = ET.Element('p')
            plist.append(p)
            p.text = '0 1 2 3' # XXX

        scenes = ET.Element('library_visual_scenes')
        root.append(scenes)

        scene = ET.Element('visual_scene')
        scenes.append(scene)
        scene.set('id', 'scene0')
        scene.set('name', 'untitled')

        node = ET.Element('node')
        scene.append(node)
        node.set('id', 'node0')
        node.set('name', 'some_node')

        inst = ET.Element('instance_geometry')
        node.append(inst)
        inst.set('url', '#geometry%d' % id(model))

        scene = ET.Element('scene')
        root.append(scene)

        inst = ET.Element('instance_visual_scene')
        scene.append(inst)
        inst.set('url', '#scene0')



        tree = ET.ElementTree(root)
        with self.mkfile(name) as file:
            tree.write(file,
                encoding='utf-8',
                xml_declaration=True,
                pretty_print=True,
            )


    def _old_extractModel(self, model):
        name = model.name + '.xml'
        root = ET.Element('model')

        eSkel = ET.Element('skeleton')
        root.append(eSkel)
        for bone in model.skeleton.bones:
            eSkel.append(self._extractBone(bone))

        eFvtxs = ET.Element('buffers')
        root.append(eFvtxs)
        for fvtx in model.fvtxs:
            eFvtxs.append(self._extractFVTX(fvtx))

        eShapes = ET.Element('shapes')
        root.append(eShapes)
        for fshp in model.fshps:
            eShapes.append(self._extractFSHP(fshp))

        eMats = ET.Element('materials')
        root.append(eMats)
        for fmat in model.fmats:
            eMats.append(self._extractFMAT(fmat))

        tree = ET.ElementTree(root)
        with self.mkfile(name) as file:
            tree.write(file,
                encoding='utf-8',
                xml_declaration=True,
                pretty_print=True,
            )


    def _extractFVTX(self, fvtx):
        elem = ET.Element('FVTX')
        # XXX the actual VTX attrib array/dict, attrs, etc
        attrs = {
            'idx': fvtx.index,
            'nvtxs': fvtx.num_vtxs,
            'nattrs': fvtx.num_attrs,
            'nbuffers': fvtx.num_bufs,
            'skin_weight_influence': fvtx.skin_weight_influence,
            'unk04': fvtx.unk04,
            'unk10': '0x%08X' % fvtx.unk10,
            'unk18': '0x%08X' % fvtx.unk18,
            'unk20': '0x%08X' % fvtx.unk20,
        }
        for k, v in attrs.items(): elem.set(k, str(v))
        for attr in fvtx.attrs:
            e = ET.Element('attribute')
            e.set('name',   attr.name)
            e.set('fmt',    '0x%04X' % attr.format)
            e.set('offset', '0x%04X' % attr.buf_offs)
            e.set('idx',    '0x%04X' % attr.buf_idx)
            e.set('unk04',  '0x%08X' % attr.unk04)
            e.set('unk0A',  '0x%04X' % attr.unk0A)
            elem.append(e)
        for vtx in fvtx.vtxs:
            e = ET.Element('vtx')
            e.set('position', '%f, %f, %f, %f' % (
                vtx.pos.x, vtx.pos.y, vtx.pos.z, vtx.pos.w))
            e.set('normal', '%f, %f, %f, %f' % (
                vtx.normal.x, vtx.normal.y, vtx.normal.z, vtx.normal.w))
            e.set('color', '%f, %f, %f, %f' % (
                vtx.color.r, vtx.color.g, vtx.color.b, vtx.color.a))
            e.set('uv', '%f, %f' % (
                vtx.texcoord.u, vtx.texcoord.v))
            e.set('idx', '0x%X, 0x%X, 0x%X, 0x%X, 0x%X' % (
                vtx.idx[0], vtx.idx[1], vtx.idx[2], vtx.idx[3], vtx.idx[4]
            ))
            e.set('weight', '%f, %f, %f, %f' % (
                vtx.weight[0], vtx.weight[1], vtx.weight[2], vtx.weight[3]
            ))
            for k, v in vtx.extra.items():
                e.set(k, str(v))
            elem.append(e)
        return elem


    def _extractFMAT(self, fmat):
        elem = ET.Element('FMAT')
        attrs = {
            'name': fmat.name,
            'unk0C': fmat.unk0C,
            'flags': fmat.mat_flags,
            'section_idx': fmat.section_idx,
            'render_info_cnt': fmat.render_info_cnt,
            'tex_ref_cnt': fmat.tex_ref_cnt,
            'sampler_cnt': fmat.sampler_cnt,
            'shader_param_volatile_cnt': fmat.shader_param_volatile_cnt,
            'source_param_data_size': fmat.source_param_data_size,
            'unkB2': fmat.unkB2,
            'unkB4': fmat.unkB4,
        }
        for k, v in attrs.items(): elem.set(k, str(v))
        return elem


    def _extractFSHP(self, fshp):
        elem = ET.Element('FSHP')
        attrs = {
            'idx':   fshp.index,
            'name':  fshp.name,
            'unk04': fshp.unk04,
            'unk08': fshp.unk08,
            'unk0C': fshp.unk0C,
            'unk30': fshp.unk30,
            'unk38': fshp.unk38,
            'unk50': fshp.unk50,
            'flags': '0x%08X' % fshp.flags,
            'single_bind': fshp.single_bind,
            'fvtx_idx': fshp.fvtx_idx,
            'skin_bone_idx_cnt': fshp.skin_bone_idx_cnt,
            'vtx_skin_cnt': fshp.vtx_skin_cnt,
            'lod_cnt': fshp.lod_cnt,
            'vis_group_cnt': fshp.vis_group_cnt,
            'fskl_array_cnt': fshp.fskl_array_cnt,
        }
        for k, v in attrs.items(): elem.set(k, str(v))
        return elem


    def _extractBone(self, bone):
        elem = ET.Element('bone')

        ePos = ET.Element('position')
        ePos.text = '%f, %f, %f' % (bone.posX, bone.posY, bone.posZ)
        elem.append(ePos)

        eScl = ET.Element('scale')
        eScl.text = '%f, %f, %f' % (
            bone.scaleX, bone.scaleY, bone.scaleZ)
        elem.append(eScl)

        eRot = ET.Element('rotation')
        eRot.text = '%f, %f, %f, %f' % (
            bone.rotX, bone.rotY, bone.rotZ, bone.rotW)
        elem.append(eRot)

        ePrt = ET.Element('parents')
        ePrt.text = '%d, %d, %d, %d' % bone.parent
        elem.append(ePrt)

        attrs = {
            'idx':   bone.bone_idx,
            'name':  bone.name,
            'flags': '0x%08X' % bone.unk22,
            'unk04': bone.unk04,
            'unk22': bone.unk22,
        }
        for k, v in attrs.items(): elem.set(k, str(v))
        return elem
