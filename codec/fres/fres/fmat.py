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
from .fresobject import FresObject
from codec.base.types import Offset, Offset64, StrOffs, Padding
from structreader import StructReader, BinaryObject
from .idxgrp import IndexGroup

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
        Offset64('shader_assign_offs'),
        Offset64('unk30_offs'),
        Offset64('tex_ref_array_offs'),
        Offset64('unk40_offs'),
        Offset64('sampler_list_offs'),
        Offset64('sampler_dict_offs'),
        Offset64('shader_param_array_offs'),
        Offset64('shader_param_dict_offs'),
        Offset64('source_param_data_offs'),
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
        ('H',  'shader_param_volatile_cnt'),
        ('H',  'source_param_data_size'),
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
        return self


    def _readDicts(self):
        dicts = ('render_param', 'sampler', 'shader_param', 'user_data')
        for name in dicts:
            offs = getattr(self, name + '_dict_offs')
            if offs:
                #d = IndexGroup().readFromFile(self.fres.file, offs)
                #log.debug("FMAT %s dict:\n%s", name, d.dump())

                # not sure these really are dicts.
                # the connections make no sense, and there doesn't
                # seem to be any reason to store these strings
                # in dicts in the first place.
                unk, cnt = self.fres.read('II', offs)
                log.debug("FMAT %s: unk=%d cnt=%d", name, unk, cnt)
                data = []
                offs += 8
                for i in range(cnt):
                    a, b, c, s, pad = self.fres.read('iHHII', offs+(i*16))
                    if s: s = self.fres.readStr(s)
                    log.debug('#%3d: %04X %04X %04X (%X) "%s"',
                        i, a, b, c, pad, s)
                    data.append({
                        'unk00': a,
                        'unk04': b,
                        'unk06': c,
                        'pad':   pad,
                        'name':  s,
                    })
            else:
                data = None
            setattr(self, name + '_dict', data)


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

            vals = []
            for j in range(cnt):
                if   typ == 0: val=self.fres.readHex(8, offs)
                elif typ == 1: val=self.fres.read('f', offs)
                elif typ == 2: val=self.fres.readStr(self.fres.read('Q', offs))
                else:
                    log.warning("Render param '%s' unknown type 0x%X",name,typ)
                    val = '<unknown>'
                vals.append(val)

            log.debug("Render param: %-5s[%d] %-32s: %s",
                typeName, cnt, name, ', '.join(map(str, vals)))

            if name in self.render_param:
                log.warning("Duplicate render param '%s'", name)
            self.renderParams[name] = vals


    def validate(self):
        super().validate()
        return True
