import io
from .base import ArchiveCodec
from ..sarc import SARC

class SarcCodec(ArchiveCodec):
    """Codec for SARC archives."""

    def list(self):
        """Print list of files in archive."""
        raise NotImplementedError

    def unpack(self, file:io.BufferedIOBase, dest:str):
        """Extract archive.

        file: File to extract.
        dest: Directory to extract to.
        """
        for file in sarc.files:
            name = self.createOutputFile(file.name)
            log.info("Extracting %s", name)
            with open(name, 'wb') as output:
                self.file.seek(file.data_start+offs)
                data = self.file.read(file.size)
                output.write(data)
        return True

    def _read(self, file):
        sarc = SARC().readFromFile(file)
        offs = sarc.header.data_offset
