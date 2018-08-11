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

class Bone(BinaryObject):
    """A bone in an FSKL."""
    # offsets in this struct are relative to the beginning of
    # the FRES file.
    # I'm assuming they're 64-bit.
    _reader = StructReader(
        ('I',  'name_offset'), # u16 len, str
        ('H',  'unk04'),
        ('H',  'unk06'),
        ('H',  'unk08'),
        ('H',  'unk0A'),
        ('H',  'unk0C'),
        ('H',  'unk0E'),
        ('H',  'unk10'),
        ('H',  'unk12'),
        ('H',  'unk14'),
        ('H',  'unk16'),
        ('H',  'bone_idx'),
        ('4h', 'parent'),
        ('H',  'unk22'),
        ('H',  'unk24'),
        ('H',  'unk26'),
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

    def readFromFile(self, file, offset=None, reader=None):
        """Read the bone from given file."""
        super().readFromFile(file, offset, reader)
        self.name = readStringWithLength(file, '<H', self.name_offset)
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
        return True
