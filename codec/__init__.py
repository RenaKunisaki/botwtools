from .base.exceptions import UnsupportedFileTypeError
from .sarc.decoder import SarcDecoder
from .yaz0.decoder import Yaz0Decoder

# File magic => encoder class
encoders = {
}

# File magic => decoder class
decoders = {
    b'SARC': SarcDecoder,
    b'Yaz0': Yaz0Decoder,
    b'Yaz1': Yaz0Decoder,
}

def getMagic(file):
    """Given a file, read the 4-byte magic ID from current position.

    This function does not change the seek position.
    """
    pos = file.tell()
    magic = file.read(4)
    file.seek(pos, 0) # reset position
    return magic

def getEncoderForFile(file):
    """Given a file, return the Encoder class for it.

    Raises UnsupportedFileTypeError if no encoder available.
    """
    magic = getMagic(file)
    enc = encoders.get(magic, None)
    if enc is None: raise UnsupportedFileTypeError(magic)
    return enc

def getDecoderForFile(file):
    """Given a file, return the Decoder class for it.

    Raises UnsupportedFileTypeError if no decoder available.
    """
    magic = getMagic(file)
    dec = decoders.get(magic, None)
    if dec is None: raise UnsupportedFileTypeError(magic)
    return dec
