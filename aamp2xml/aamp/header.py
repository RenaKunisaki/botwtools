import logging; log = logging.getLogger()
from structreader import StructReader, BinaryObject

class Header(BinaryObject):
    """AAMP file header."""
    _reader = StructReader(
        ('4s', 'magic'), # 'AAMP'
        ('I', 'version'),
        ('I', 'unk08'),
        ('I', 'filesize'),
        ('I', 'unk10'),
        ('I', 'xml_str_len'),
        ('I', 'num_root_nodes'),
        ('I', 'num_children'), # num direct children of root node
        ('I', 'total_nodes'),
        ('I', 'data_buf_size'),
        ('I', 'str_buf_size'),
        ('I', 'unk2C'),
        ('4s','str_xml'),
    )

    def validate(self):
        assert self.magic == b'AAMP', "Not an AAMP file"
        assert self.version == 2, \
            "Unsupported version: " + str(self.version)

        if self.str_xml != b'xml\0':
            log.warn("Header XML string is %s, should be b'xml\0'",
                self.str_xml)

        log.debug("AAMP filesize:        %d", self.filesize)
        log.debug("AAMP #roots:          %d", self.num_root_nodes)
        log.debug("AAMP #root children:  %d", self.num_children)
        log.debug("AAMP total nodes:     %d", self.total_nodes)
        log.debug("AAMP data buf size:   %d", self.data_buf_size)
        log.debug("AAMP string buf size: %d", self.str_buf_size)
