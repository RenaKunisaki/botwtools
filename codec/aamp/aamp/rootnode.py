import logging; log = logging.getLogger()
from lxml import etree as ET
from structreader import StructReader, BinaryObject
from .types import aamp_data_type
from .node import Node

class RootNode(Node):
    """AAMP root node."""
    _reader = StructReader(
        ('I', 'name_hash'), # always 0xA4F6CB6C (<param_root>)
        ('I', 'unk04'), # 0x3
        ('H', 'data_offset'), # relative to start of node
        ('H', 'num_children'),
    )

    def validate(self):
        if self.name_hash != 0xA4F6CB6C:
            log.warn("Root name_hash is 0x%08X, should be 0xA4F6CB6C",
                self.name_hash)
        log.debug("AAMP root unk04=%d, data=0x%04X, nChild=%d",
            self.unk04, self.data_offset, self.num_children)
        return super().validate()


    def toXML(self, _depth=0):
        """Convert node to XML node object."""
        elem = super().toXML(_depth=_depth+1)
        elem.set('{'+self.xmlns+'}unk04', str(self.unk04))
        return ET.ElementTree(elem)


    def __str__(self):
        return "<AAMP root node '%s' at 0x%x>" % (self.name, id(self))
