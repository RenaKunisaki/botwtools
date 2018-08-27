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
from structreader import StructReader, BinaryObject
from .idxgrp import IndexGroup

shaderParamTypes = {
    # http://mk8.tockdom.com/wiki/FMDL_(File_Format)#Material_Parameter
    0x08: {'fmt':'I',  'name':'ptr',   'outfmt':'%08X'},
    0x0C: {'fmt':'f',  'name':'float', 'outfmt':'%f'},
    0x0D: {'fmt':'2f', 'name':'Vec2f', 'outfmt':'%f, %f'},
    0x0E: {'fmt':'3f', 'name':'Vec3f', 'outfmt':'%f, %f, %f'},
    0x0F: {'fmt':'4f', 'name':'Vec4f', 'outfmt':'%f, %f, %f, %f'},
    0x1E: {'fmt':'I5f','name':'texSRT', # scale, rotation, translation
        'outfmt':'mode=%d XS=%f YS=%f rot=%f X=%f Y=%f'},
}

class ShaderAssign(FresObject):
    _reader = StructReader(
        StrOffs('name'), Padding(4),
        StrOffs('name2'), Padding(4),
        Offset64('vtx_attr_names'), # -> offsets of attr names
        Offset64('vtx_attr_dict'),
        Offset64('tex_attr_names'),
        Offset64('tex_attr_dict'),
        Offset64('mat_param_vals'), # names from dict
        Offset64('mat_param_dict'),
        Padding(4),
        ('B', 'num_vtx_attrs'),
        ('B', 'num_tex_attrs'),
        ('H', 'num_mat_params'),
    )

class FMAT(FresObject):
    """A FMAT in an FMDL."""
    _magic = b'FMAT'
    _reader = StructReader(
        ('4s', 'magic'),
        ('I',  'size'),
        ('I',  'size2'),
        Padding(4),
        StrOffs('name'),
        Padding(4),
        Offset64('render_param_offs'),
        Offset64('render_param_dict_offs'),
        Offset64('shader_assign_offs'), # -> name offsets
        Offset64('unk30_offs'),
        Offset64('tex_ref_array_offs'),
        Offset64('unk40_offs'),
        Offset64('sampler_list_offs'),
        Offset64('sampler_dict_offs'),
        Offset64('shader_param_array_offs'),
        Offset64('shader_param_dict_offs'),
        Offset64('shader_param_data_offs'),
        Offset64('user_data_offs'),
        Offset64('user_data_dict_offs'),
        Offset64('volatile_flag_offs'),
        Offset64('user_offs'),
        Offset64('sampler_slot_offs'),
        Offset64('tex_slot_offs'),
        ('I',  'mat_flags'),
        ('H',  'section_idx'),
        ('H',  'render_param_cnt'),
        ('B',  'tex_ref_cnt'),
        ('B',  'sampler_cnt'),
        ('H',  'shader_param_cnt'),
        ('H',  'shader_param_data_size'),
        ('H',  'raw_param_data_size'),
        ('H',  'user_data_cnt'),
        Padding(2),
        ('I',  'unkB4'),
        size = 0xB8,
    )

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the FMAT from given FRES."""
        super().readFromFRES(fres, offset, reader)
        log.debug("FMAT name='%s'", self.name)
        self.dumpToDebugLog()
        self.dumpOffsets()
        self._readDicts()
        self._readRenderParams()
        self._readShaderParams()
        self._readTextureList()
        self._readSamplerList()
        self._readShaderAssign()

        return self


    def _readDicts(self):
        dicts = ('render_param', 'sampler', 'shader_param', 'user_data')
        for name in dicts:
            offs = getattr(self, name + '_dict_offs')
            if offs:
                #d = IndexGroup().readFromFile(self.fres.file, offs)
                #log.debug("FMAT %s dict:\n%s", name, d.dump())
                data = self._readDict(offs, name)
            else:
                data = None
            setattr(self, name + '_dict', data)


    def _readDict(self, offs, name):
        unk, cnt = self.fres.read('II', offs)
        log.debug("FMAT dict %s: unk=0x%X cnt=%d", name, unk, cnt)
        data = []
        offs += 8
        for i in range(cnt+1): # +1 for root node
            search, left, right, name, pad = self.fres.read(
                'iHHII', offs+(i*16))
            if name: name = self.fres.readStr(name)
            else: name = None
            #log.debug('#%3d: %04X (%d:%d) %04X %04X (%X) "%s"',
            #    i, search, search >> 3, search & 7,
            #    left, right, pad, name)
            data.append({
                'search': search,
                'left':   left,
                'right':  right,
                'pad':    pad,
                'name':   name,
            })
        return data


    def _readTextureList(self):
        self.textures = []
        log.debug("Texture list:")
        for i in range(self.tex_ref_cnt):
            name = self.fres.readStrPtr(self.tex_ref_array_offs + (i*8))
            slot = self.fres.read('q', self.tex_slot_offs + (i*8))
            log.debug("%3d (%2d): %s", i, slot, name)
            self.textures.append({'name':name, 'slot':slot})


    def _readSamplerList(self):
        self.samplers = []
        log.debug("Sampler list:")
        for i in range(self.sampler_cnt):
            data = self.fres.readHexWords(8, self.sampler_list_offs + (i*32))
            slot = self.fres.read('q', self.sampler_slot_offs + (i*8))
            log.debug("%3d (%2d): %s", i, slot, data)
            self.samplers.append({'slot':slot, 'data':data})
            # XXX no idea what to do with this data


    def _readRenderParams(self):
        self.renderParams = {}
        types = ('?', 'float', 'str')
        for i in range(self.render_param_cnt):
            name, offs, cnt, typ, pad = self.fres.read('QQHHI',
                self.render_param_offs + (i*24))
            name = self.fres.readStr(name)

            if pad != 0:
                log.warning("Render info '%s' padding=0x%X", name, pad)
            try: typeName = types[typ]
            except IndexError: typeName = '0x%X' % typ

            param = {
                'name':  name,
                'count': cnt,
                'type':  types[typ],
                'vals':  [],
            }
            for j in range(cnt):
                if   typ == 0: val=self.fres.readHex(8, offs)
                elif typ == 1: val=self.fres.read('f', offs)
                elif typ == 2: val=self.fres.readStrPtr(offs)
                else:
                    log.warning("Render param '%s' unknown type 0x%X",name,typ)
                    val = '<unknown>'
                param['vals'].append(val)

            log.debug("Render param: %-5s[%d] %-32s: %s",
                typeName, cnt, name, ', '.join(map(str, param['vals'])))

            if name in self.renderParams:
                log.warning("Duplicate render param '%s'", name)
            self.renderParams[name] = param


    def _readShaderParams(self):
        self.shaderParams = {}
        log.debug("Shader params:")

        array_offs = self.shader_param_array_offs
        data_offs  = self.shader_param_data_offs
        for i in range(self.shader_param_cnt):
            # unk0: always 0; unk14: always -1
            # idx0, idx1: both always == i
            unk0, name, type, size, offset, unk14, idx0, idx1 = \
                self.fres.read('QQBBHiHH', array_offs + (i*32))

            name = self.fres.readStr(name)
            type = shaderParamTypes[type]
            if unk0: log.debug("Shader param '%s' unk0=0x%X", name, unk0)
            if unk14 != -1:
                log.debug("Shader param '%s' unk14=%d", name, unk14)
            if idx0 != i or idx1 != i:
                log.debug("Shader param '%s' idxs=%d, %d (expected %d)",
                    name, idx0, idx1, i)

            data = self.fres.read(size, data_offs + offset)
            data = struct.unpack(type['fmt'], data)

            log.debug("%-38s %-5s %s", name, type['name'],
                type['outfmt'] % data)

            if name in self.shaderParams:
                log.warning("Duplicate shader param '%s'", name)

            self.shaderParams[name] = {
                'name':   name,
                'type':   type,
                'size':   size,
                'offset': offset,
                'idxs':   (idx0, idx1),
                'unk00':  unk0,
                'unk14':  unk14,
                'data':   data,
            }


    def _readShaderAssign(self):
        assign = ShaderAssign()
        assign.readFromFRES(self.fres, self.shader_assign_offs)
        self.shader_assign = assign

        log.debug("shader assign: %d vtx attrs, %d tex attrs, %d mat params",
            assign.num_vtx_attrs, assign.num_tex_attrs,
            assign.num_mat_params)

        self.vtxAttrs = []
        for i in range(assign.num_vtx_attrs):
            name = self.fres.readStrPtr(assign.vtx_attr_names + (i*8))
            log.debug("vtx attr %d: '%s'", i, name)
            self.vtxAttrs.append(name)

        self.texAttrs = []
        for i in range(assign.num_tex_attrs):
            name = self.fres.readStrPtr(assign.tex_attr_names + (i*8))
            log.debug("tex attr %d: '%s'", i, name)
            self.texAttrs.append(name)

        self.mat_param_dict = self._readDict(
            assign.mat_param_dict, "mat_params")
        self.mat_params = {}
        log.debug("material params:")
        for i in range(assign.num_mat_params):
            name = self.mat_param_dict[i+1]['name']
            val  = self.fres.readStrPtr(assign.mat_param_vals + (i*8))
            log.debug("%-40s: %s", name, val)
            if name in self.mat_params:
                log.warning("duplicate mat_param '%s'", name)
            self.mat_params[name] = val

    def validate(self):
        super().validate()
        return True
