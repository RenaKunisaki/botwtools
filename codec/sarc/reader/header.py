import logging; log = logging.getLogger()
from structreader import StructReader, BinaryObject

class Header(BinaryObject):
    """SARC file header."""
    _reader = StructReader(
        ('4s', 'magic'), # 'SARC'
        ('H',  'header_len'), # always 0x14
        ('H',  'byte_order'), # 0xFEFF or 0xFFFE
        ('I',  'file_size'),
        ('I',  'data_offset'),
        ('H',  'version'), # always 0x0100
        ('H',  'reserved12'),
    )

    def validate(self):
        assert self.magic == b'SARC', "Not a SARC file"
        assert self.version == 0x0100, \
            "Unsupported version: " + str(self.version)
        assert self.byte_order in (0xFEFF, 0xFFFE), \
            "Invalid byte order mark: 0x%04X" % self.byte_order

        if self.header_len != 0x14:
            log.warn("SARC header length is %d, should be 20",
                self.header_len)
        if self.reserved12 != 0:
            log.warn("SARC reserved field 0x12 is %d, should be 0",
                self.reserved12)

        return True
