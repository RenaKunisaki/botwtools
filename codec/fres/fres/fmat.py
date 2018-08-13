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

class FMAT(FresObject):
    """A FMAT in an FMDL."""
    _magic = b'FMAT'
    _reader = StructReader(
        ('4s', 'magic'),
        ('I',  'size'),
        ('I',  'size2'),
        ('I',  'unk0C'),
        StrOffs('name'),
        Padding(4),
        Offset64('render_info_offs'),
        Offset64('render_info_dict_offs'),
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
        ('H',  'render_info_cnt'),
        ('B',  'tex_ref_cnt'),
        ('B',  'sampler_cnt'),
        ('H',  'shader_param_volatile_cnt'),
        ('H',  'source_param_data_size'),
        ('H',  'raw_param_data_size'),
        ('H',  'user_data_cnt'),
        Padding(2),
        ('I',  'unkB4'),
    )

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the FMAT from given FRES."""
        super().readFromFRES(fres, offset, reader)
        #log.debug("FMAT name='%s'", self.name)
        #self.dumpToDebugLog()
        #self.dumpOffsets()

        return self


    def validate(self):
        super().validate()
        return True
