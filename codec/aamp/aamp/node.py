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
from lxml import etree as ET
from structreader import StructReader, BinaryObject
from .types import read_aamp_type, get_type_name
from .names import getName

xmlns = 'https://github.com/jam1garner/aamp2xml' # XXX
xmlnsmap = {
    'aamp': xmlns,
}

class Node(BinaryObject):
    """AAMP node."""
    xmlns      = xmlns
    xmlnsmap   = xmlnsmap
    isListable = False

    _reader = StructReader(
        ('I', 'name_hash'),
        ('H', 'data_offset'),
        ('B', 'num_children'),
        ('B', 'data_type'),
    )

    def __init__(self, file=None):
        """Create new Node.

        file: File to read it from. (optional)
        """
        self.children = []
        self.data     = None
        if file is not None: self.readFromFile(file)


    def readFromFile(self, file):
        """Read the node from the given file."""
        super().readFromFile(file)

        curPos = file.tell()
        offset = (self.data_offset * 4) - self._reader.size
        file.seek(offset, 1)

        if self.num_children > 0:
            for i in range(self.num_children):
                self.children.append(Node(file))
        elif hasattr(self, 'data_type'):
            self.data = read_aamp_type(file, self.data_type)
        else: # root node
            pass

        file.seek(curPos) # restore position
        self.name = getName(self.name_hash)


    def toXML(self, _depth=0):
        """Convert node to XML node object."""
        elem = ET.Element(self.name, nsmap=self.xmlnsmap)
        #elem.set('{'+self.xmlns+'}namehash',
        #    '%08X' % self.name_hash)

        if self.num_children > 0:
            for child in self.children:
                elem.append(child.toXML())
        elif hasattr(self, 'data_type'):
            elem.set('type', get_type_name(self.data_type))
            try:
                elem.text = str(self.data)
            except ValueError:
                log.error("Error writing string to XML: %s", self.data)
        else: # root node
            pass

        return elem


    def __str__(self):
        return "<AAMP node '%s' at 0x%x>" % (self.name, id(self))
