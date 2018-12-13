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
import math
import numpy as np
from vmath import Matrix, Vec3, Vec4, Quaternion
from ..types import attrFmts
E = myxml.Element

class X3DWriter:
    """Takes objects found in an FRES and creates
    an X3D file from them.
    """
    def __init__(self, fres):
        self.fres = fres

        #for i, fmat in enumerate(self.fmats):
        #    writer.addFMAT(fmat)

        #for i, fvtx in enumerate(self.fvtxs):
        #    writer.addFVTX(fvtx, name=self.fshps[i].name)
        #    writer.addFSHP(self.fshps[i]) # XXX this is weird

        #writer.addFSKL(self.skeleton)
        #writer.addScene()


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

                    # Strip W coordinate from position buffers.
                    if attr.name == '_p0': data = data[0:3]

                    # flip texture Y coord because COLLADA is backward
                    # from what everything else uses
                    #elif attr.name in ('_u0', '_u1'):
                    #    data = (data[0], fmt.get('max', 1) - data[1])

                    if type(data) in (list, tuple):
                        attr_buffers[attr.name] += data
                    else: attr_buffers[attr.name].append(data)

        #for name, buf in attr_buffers.items():
        #    log.debug("%s: %s", name, buf)
        return attr_buffers


    def _makeHead(self):
        """Make the <head> for the X3D document."""
        return E('head',
            E('meta', name='filename',  content='XXX'),
            E('meta', name='title',     content=self.fres.name),
            E('meta', name='generator', content="https://github.com/RenaKunisaki/botwtools"),
            profile='Core', version='3.3',
        )


    def _makeAppearance(self, fshp, lod):
        """Make Appearance element for an LOD of an FSHP."""
        appearance = E('Appearance')
        material = appearance.Child('Material')

        fmat = self.fres.fmats[fshp.fmat_idx]
        for tex in fmat.textures:
            appearance.Child('ImageTexture',
                url='./textures/%s.png' % tex['name'])

        return appearance


    def _makeShape(self, fshp):
        """Make element for an FSHP."""
        xfrm = E('Transform', DEF=fshp.name)
        for j, lod in enumerate(fshp.lods):
            fvtx    = self.fres.fvtxs[fshp.fvtx_idx]
            buffers = self._getAttrBuffers(lod, fvtx)
            pos     = buffers['_p0']

            # Make Shape node.
            shape   = xfrm.Child('Shape',
                DEF='%s.lod%d' % (fshp.name, j),
            )

            # Make Appearance node.
            shape.append(self._makeAppearance(fshp, lod))

            # Make polygon nodes. XXX support other formats
            shape.Child('IndexedTriangleSet', solid='true',
                index=' '.join(map(str, lod.idx_buf))) \
                .Child('Coordinate',
                    point=' '.join(map(lambda f: '%f'%f, pos)),
                )
        return xfrm


    def toXML(self):
        """Generate XML document for this file."""
        document = myxml.Document('X3D')
        #document.addNamespace(
        #    'xsd','http://www.w3.org/2001/XMLSchema-instance')
        #document.addNamespace(
        #    'xsd:noNamespaceSchemaLocation',
        #    'http://www.web3d.org/specifications/x3d-3.3.xsd')

        root = document.root
        #root.set({
        #    'xmlns:xsd': 'http://www.w3.org/2001/XMLSchema-instance',
        #    'xsd:noNamespaceSchemaLocation': #'http://www.web3d.org/specifications/x3d-3.3.xsd',
        #})
        root.append(self._makeHead())
        scene = root.Child('Scene')

        # Transform > Group > Shape > Appearance > Material
        # Transform > Group > Shape > IndexedFaceSet > Coordinate

        for i, fshp in enumerate(self.fres.fshps):
            scene.append(self._makeShape(fshp))

        #for scene in self.scenes:
        #    root.Child('scene')
        return document
