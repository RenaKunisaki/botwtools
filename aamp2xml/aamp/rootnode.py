import logging; log = logging.getLogger()
from structreader import StructReader, BinaryObject
from .types import aamp_data_type
from .node import Node

class RootNode(Node):
    """AAMP root node."""
    _reader = StructReader(
        ('I', 'node_id'), # always 0xA4F6CB6C (<param_root>)
        ('I', 'unk04'), # 0x3
        ('H', 'data_offset'), # relative to start of node
        ('H', 'num_children'),
    )

    def validate(self):
        if self.node_id != 0xA4F6CB6C:
            log.warn("Root node ID is 0x%08X, should be 0xA4F6CB6C",
                self.node_id)
        log.debug("AAMP root unk04=%d, data=0x%04X, nChild=%d",
            self.unk04, self.data_offset, self.num_children)
        return super().validate()
