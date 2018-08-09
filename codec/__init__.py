from .base.exceptions import UnsupportedFileTypeError
from .sarc.decoder import SarcDecoder
from .yaz0.decoder import Yaz0Decoder

encoders = {
}

decoders = {
    b'SARC': SarcDecoder,
    b'Yaz0': Yaz0Decoder,
    b'Yaz1': Yaz0Decoder,
}

def getMagic(file):
    pos = file.tell()
    magic = file.read(4)
    file.seek(pos, 0) # reset position
    return magic

def getEncoderForFile(file):
    magic = getMagic(file)
    enc = encoders.get(magic, None)
    if enc is None: raise UnsupportedFileTypeError(magic)
    return enc

def getDecoderForFile(file):
    magic = getMagic(file)
    dec = decoders.get(magic, None)
    if dec is None: raise UnsupportedFileTypeError(magic)
    return dec
