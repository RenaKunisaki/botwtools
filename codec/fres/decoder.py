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
import io
import sys
import struct
import myxml
from filereader import FileReader
from ..base import ArchiveDecoder, UnsupportedFileTypeError, TxtOutput
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
        """Export model to COLLADA file."""
        name = model.name + '.dae'

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

        # geometries
        geoms = root.Child('library_geometries')


        # mesh
        geom_ids = []
        model_names = []
        for fvtx in model.fvtxs:
            gid = 'geometry%d' % id(fvtx)
            geom_ids.append(gid)
            geom  = geoms.Child('geometry',
                id = gid,
                name = model.name,
            )
            mesh = geom.Child('mesh')

            for attr in fvtx.attrs:
                self._exportAttribute(mesh, fvtx, attr)

            vtxs = mesh.Child('vertices',
                id = 'vertices%d' % id(mesh),
            )
            input = vtxs.Child('input',
                semantic = 'POSITION',
                source = '#src__p0',
            )
            # XXX export each LOD as a separate model
            # but how do we share the buffers?
            for fshp in model.fshps:
                model_names.append(fshp.name)
                for lod in fshp.lods:
                    self._exportLod(mesh, lod)
                    #break # only export first model
                #break

        # define a scene containing the model
        scenes = root.Child('library_visual_scenes')
        scene  = scenes.Child('visual_scene',
            id   = 'scene0',
            name = 'untitled',
        )
        for i, gid in enumerate(geom_ids):
            node = scene.Child('node',
                id   = 'node_'+gid,
                name = model_names[i],
            )
            node.Child('instance_geometry',
                url = '#'+gid,
            )
        scene = root.Child('scene')
        inst  = scene.Child('instance_visual_scene',
            url = '#scene0',
        )

        # write document to file
        with self.mkfile(name) as file:
            document.writeToFile(file, pretty_print=True)


    def _exportAttribute(self, parent, fvtx, attr):
        src = parent.Child('source',
            id = 'src_' + attr.name,
            name = attr.name,
            #unk04 = '0x%08X' % attr.unk04,
            #unk0A = '0x%04X' % attr.unk0A,
        )
        buf  = fvtx.buffers[attr.buf_idx]
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

        # stupid
        if attr.name == '_p0':
            data = self._fixBufferForBlender(data)

        self._makeArrayForAttribute(src, attr, data)
        self._makeAccessorForAttribute(src, attr, data)



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


    def _makeArrayForAttribute(self, parent, attr, data):
        # XXX use attr.format instead of always float
        arr = parent.Child('float_array',
            id = 'array%d' % id(attr),
            count = len(data),
        )
        arr.text = ' '.join(map(str, data))


    def _makeAccessorForAttribute(self, parent, attr, data):
        # XXX support more types of accessor/technique
        offs = attr.buf_offs #* buf.stride
        tech = parent.Child('technique_common')
        acc  = tech.Child('accessor',
            count  = len(data)*3, # XXX what is this
            offset = offs,
            stride = '3',
            source = '#array%d' % id(attr),
        )
        for p in ('X', 'Y', 'Z'):
            acc.Child('param', name=p, type='float')


    def _exportLod(self, parent, lod):
        # <lines>, <linestrips>, <polygons>, <polylists>, <triangles>, <trifans> and <tristrips>
        if lod.prim_fmt in ('line_strip', 'line_loop'):
            #elem = 'lines'
            elem = 'triangles'
        elif lod.prim_fmt == 'triangles':
            elem = 'triangles'
        else:
            log.error("Unsupported prim fmt %s", lod.prim_fmt)
            return
        plist = parent.Child(elem,
            count = len(lod.faces),
        )
        inp_vtx = plist.Child('input',
            offset = '0',
            semantic = 'VERTEX',
            source = '#vertices%d' % id(parent),
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
