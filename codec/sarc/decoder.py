import logging; log = logging.getLogger()
import io
import sys
import struct
from ..base import ArchiveDecoder, FileReader, UnsupportedFileTypeError
from .reader import SARC

class SarcDecoder(ArchiveDecoder):
    """Decoder for SARC archive."""

    def _read(self):
        self.archive = SARC().readFromFile(self.input)

    def _iter_objects(self):
        return iter(self.archive.files)

    def _get_num_objects(self):
        return self.archive.fatHeader.node_count

    def printList(self, dest=sys.stdout):
        """Print nicely formatted list of this file's objects."""
        print("Files:", self.numObjects)
        print("NameHash  FileSize Name")
        for obj in self.objects:
            print("%08X %9d %s" % (obj.name_hash, obj.size, obj.name))
