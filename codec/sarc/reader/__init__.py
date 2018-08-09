import logging; log = logging.getLogger()
from structreader import StructReader, BinaryObject, readString
from .header      import Header
from .nametblhdr  import NameTableHeader
from .sfatheader  import SFATHeader
from .sfatnode    import SFATNode


class File:
    """Represents a file in a SARC archive."""
    def __init__(self, arc, node, name):
        self.archive    = arc
        self.name       = name
        self.name_hash  = node.name_hash
        self.attrs      = node.file_attrs
        self.data_start = node.data_start
        self.data_end   = node.data_end
        self.size       = self.data_end - self.data_start

    def read(self, size=-1, offset=0):
        """Read bytes from the file."""
        if size < 0: size = self.size - offset
        if offset >= self.size: return b''
        src = self.archive.file
        src.seek(self.data_start + self.archive.header.data_offset + offset)
        return src.read(size)

    def __str__(self):
        return "<File:%s at 0x%x>" % (self.name, id(self))


class SARC:
    def __init__(self):
        self.files = []
        self.nodes = []

    def readFromFile(self, file):
        """Read the archive from given file."""
        self.file      = file
        self.header    = Header().readFromFile(file)
        self.fatHeader = SFATHeader().readFromFile(file)

        log.debug("SARC BOM=0x%04X, node count=%d, data offs=0x%X",
            self.header.byte_order, self.fatHeader.node_count,
            self.header.data_offset)

        # XXX do something with the BOM
        # FEFF = big endian, FFFE = little
        assert self.header.byte_order == 0xFEFF, \
            "little endian support not implemented yet, sorry"

        # read nodes
        for i in range(self.fatHeader.node_count):
            self.nodes.append(SFATNode().readFromFile(file))

        # read nametable
        self.nametable = NameTableHeader().readFromFile(file)
        self.nametable_offset = file.tell()

        # read names and build File objects
        for i, node in enumerate(self.nodes):
            name = 'file' + str(i)
            if node.name_offset is not None:
                name = self._readName(file, node.name_offset)
            self.files.append(File(self, node, name))

        return self

    def _readName(self, file, offs):
        """Read the name of a file from given offset
        in nametable in given file.
        """
        file.seek(self.nametable_offset + offs, 0)
        return readString(file)
