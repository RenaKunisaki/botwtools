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
from .types import aamp_data_type
from .node import Node

class RootNode(Node):
    """AAMP root node."""
    _reader = StructReader(
        ('I', 'name_hash'),
        ('H', 'unk04'),
        ('H', 'unk06'),
        ('H', 'data_offset'), # relative to start of node
        ('H', 'num_children'),
    )

    def validate(self):
        #if self.name_hash != 0xA4F6CB6C:
        #    log.warn("Root name_hash is 0x%08X, should be 0xA4F6CB6C",
        #        self.name_hash)
        log.debug("AAMP root unk04=0x%08X, data=0x%04X, nChild=%d",
            self.unk04, self.data_offset, self.num_children)
        return super().validate()


    def toXML(self, _depth=0):
        """Convert node to XML node object."""
        elem = super().toXML(_depth=_depth+1)
        elem.set('{'+self.xmlns+'}unk04', str(self.unk04))
        elem.set('{'+self.xmlns+'}unk06', str(self.unk06))
        return elem


    def __str__(self):
        return "<AAMP root node '%s' at 0x%x>" % (self.name, id(self))
