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

import struct
from .base.exceptions import UnsupportedFileTypeError
from .aamp.decoder import AampDecoder
from .bntx.decoder import BntxDecoder
from .byml.decoder import BymlDecoder
from .fres.decoder import FresDecoder
from .sarc.decoder import SarcDecoder
from .yaz0.decoder import Yaz0Decoder

# File magic => encoder class
encoders = {
}

# File magic => decoder class
decoders = {
    b'AAMP': AampDecoder,
    b'BNTX': BntxDecoder,
    b'BY':   BymlDecoder,
    b'SARC': SarcDecoder,
    b'FRES': FresDecoder,
    b'Yaz0': Yaz0Decoder,
    b'Yaz1': Yaz0Decoder,
    b'YB':   BymlDecoder,
}

def findClass(file, classes):
    """Given a file and a dict of {magic:class}, try to find a class
    that supports this file.

    Reads file "magic" identifiers from the current position.
    Restores the position afterward.

    Returns the class, or throws UnsupportedFileTypeError.
    """
    pos = file.tell()
    for magic, cls in classes.items():
        try:
            m = file.read(len(magic))
            file.seek(pos, 0) # restore position
            if m == magic: return cls
        except struct.error: # file is shorter than magic
            pass

    # no match found
    try:
        m = file.read(4)
    except struct.error:
        log.error("File is less than 4 bytes")
        m = b''
    file.seek(pos, 0) # restore position
    raise UnsupportedFileTypeError(m)


def getEncoderForFile(file):
    """Given a file, return the Encoder class for it.

    Raises UnsupportedFileTypeError if no encoder available.
    """
    return findClass(file, encoders)


def getDecoderForFile(file):
    """Given a file, return the Decoder class for it.

    Raises UnsupportedFileTypeError if no decoder available.
    """
    return findClass(file, decoders)
