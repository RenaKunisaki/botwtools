import logging; log = logging.getLogger()
from structreader import StructReader, BinaryObject

class SFATNode(BinaryObject):
    """SARC file SFAT file node."""
    _reader = StructReader(
        ('I',  'name_hash'), # filename hash
        ('I',  'file_attrs'),
        ('I',  'data_start'), # file data offs relative to SARC header data_offset
        ('I',  'data_end'),
    )

    def readFromFile(self, file):
        """Read the node from the given file."""
        super().readFromFile(file)
        if self.file_attrs & 0x01000000:
            self.name_offset = (self.file_attrs & 0xFFFF) * 4
        else:
            self.name_offset = None
        return self


    def validate(self):
        assert self.data_start <= self.data_end, \
            "File size is negative"
        return True
