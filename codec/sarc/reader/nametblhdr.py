import logging; log = logging.getLogger()
from structreader import StructReader, BinaryObject

class NameTableHeader(BinaryObject):
    """SARC file SFAT filename table header."""
    _reader = StructReader(
        ('4s', 'magic'), # 'SFNT'
        ('H',  'header_len'), # always 8
        ('H',  'reserved06'),
    )

    def validate(self):
        assert self.magic == b'SFNT', "Not an SFNT object"
        if self.reserved06 != 8:
            log.warn("SFNT reserved06 is %d, should be 8",
                self.reserved06)
        return True
