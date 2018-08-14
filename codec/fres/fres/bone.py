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
from structreader import StructReader, BinaryObject
from .fresobject import FresObject
from .types import Offset, Offset64, StrOffs, Padding

class Bone(FresObject):
    """A bone in an FSKL."""
    # offsets in this struct are relative to the beginning of
    # the FRES file.
    # I'm assuming they're 64-bit.
    _reader = StructReader(
        StrOffs('name'),
        ('5I',  'unk04'),
        ('H',  'bone_idx'),
        ('4h', 'parent'),
        Padding(2),
        ('I',  'flags'),
        ('f',  'scaleX'),
        ('f',  'scaleY'),
        ('f',  'scaleZ'),
        ('f',  'rotX'),
        ('f',  'rotY'),
        ('f',  'rotZ'),
        ('f',  'rotW'),
        ('f',  'posX'),
        ('f',  'posY'),
        ('f',  'posZ'),
    )

    def readFromFRES(self, fres, offset=None, reader=None):
        """Read the bone from given FRES."""
        super().readFromFRES(fres, offset, reader)
        #self.s60  = readStringWithLength(file, '<H', self.unk60)
        #self.s70  = readStringWithLength(file, '<H', self.unk70)
        #self.s88  = readStringWithLength(file, '<H', self.unk88)

        #log.debug("Bone name  = '%s'", self.name)
        #log.debug("Bone s60   = '%s'", self.s60)
        #log.debug("Bone s70   = '%s'", self.s70)
        #log.debug("Bone s88   = '%s'", self.s88)

        #self.dumpToDebugLog()
        return self


    def validate(self):
        super().validate()
        return True