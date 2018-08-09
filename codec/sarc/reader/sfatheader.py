import logging; log = logging.getLogger()
from structreader import StructReader, BinaryObject

class SFATHeader(BinaryObject):
    """SARC file SFAT structure header."""
    _reader = StructReader(
        ('4s', 'magic'), # 'SFAT'
        ('H',  'header_len'), # always 0xC
        ('H',  'node_count'),
        ('I',  'hash_key'), # always 0x65
    )

    def validate(self):
        assert self.magic == b'SFAT', "Not a SFAT header"

        if self.header_len != 0xC:
            log.warn("SFAT header length is %d, should be 12",
                self.header_len)
        if self.hash_key != 0x65:
            log.warn("SFAT hash_key is 0x%X, should be 0x65",
                self.hash_key)

        return True
