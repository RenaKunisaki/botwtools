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
from structreader import StructReader, BinaryObject, readStringWithLength

class FMAT(BinaryObject):
    """A FMAT in an FMDL."""
    _reader = StructReader(
        ('4s', 'magic'),  # 'FMAT'
        ('I',  'size'),
        ('I',  'size2'),
        ('I',  'unk0C'),
        ('Q',  'name_offset'),
        ('Q',  'render_info_offs'),
        ('Q',  'render_info_dict_offs'),
        ('Q',  'shader_assign_offs'),
        ('Q',  'unk30_offs'),
        ('Q',  'tex_ref_array_offs'),
        ('Q',  'unk40_offs'),
        ('Q',  'sampler_list_offs'),
        ('Q',  'sampler_dict_offs'),
        ('Q',  'shader_param_array_offs'),
        ('Q',  'shader_param_dict_offs'),
        ('Q',  'source_param_data_offs'),
        ('Q',  'user_data_offs'),
        ('Q',  'user_data_dict_offs'),
        ('Q',  'volatile_flag_offs'),
        ('Q',  'user_offs'),
        ('Q',  'sampler_slot_offs'),
        ('Q',  'tex_slot_offs'),
        ('I',  'mat_flags'),
        ('H',  'section_idx'),
        ('H',  'render_info_cnt'),
        ('B',  'tex_ref_cnt'),
        ('B',  'sampler_cnt'),
        ('H',  'shader_param_volatile_cnt'),
        ('H',  'source_param_data_size'),
        ('H',  'raw_param_data_size'),
        ('H',  'user_data_cnt'),
        ('H',  'unkB2'),
        ('I',  'unkB4'),
    )

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the FMAT from given FRES."""
        super().readFromFile(fres.file, offset, reader)
        self.fres = fres
        self.name = readStringWithLength(fres.file,
            '<H', self.name_offset)
        log.debug("FMAT name='%s'", self.name)
        self.dumpToDebugLog()
        self.dumpOffsets()

        return self


    def validate(self):
        assert self.magic == b'FMAT', "Not an FMAT"
        return True
