#!/usr/bin/env python3
import struct
import sys
import io
import os
# hack to import from parent dir
sys.path.append(os.path.dirname(os.path.realpath(__file__))+'/..')
import logger; logger.setup('aamp2xml')
log = logger.logging.getLogger()

from .aamp import Header, Node, RootNode

def validate_file_size(file, header):
    """Make sure file size matches what header says it is."""
    try:
        pos  = file.tell()
        size = file.seek(0, 2)
        file.seek(pos, 0) # return to original position
        if header.filesize != size:
            log.warn("AAMP header says filesize is %d, but it's actually %d",
                header.filesize, size)
            return False
    except io.UnsupportedOperation:
        # can't seek; this is probably stdin or such
        pass
    return True


def read_aamp(file):
    """Read AAMP file and return XML representation."""
    header = Header().readFromFile(file)
    validate_file_size(file, header)

    root = RootNode(file)
    return root.toXML()


if __name__ == '__main__':
    with open(sys.argv[1], 'rb') as file:
        print(read_aamp(file))
