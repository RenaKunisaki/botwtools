import logging; log = logging.getLogger()
import io
import sys
import struct
from .decoder import Decoder

class ArchiveDecoder(Decoder):
    """Base class for decoders for archive files (files which
    may contain more than one file).
    """
    def unpack(self):
        nobj = self.numObjects
        for i, obj in enumerate(self.objects):
            name = getattr(obj, 'name', '%d.bin' % i)
            log.info("[%3d/%3d] Extracting %s...", i+1, nobj, name)
            self.writeFile(name, obj.read())
