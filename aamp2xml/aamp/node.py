import logging; log = logging.getLogger()
from structreader import StructReader, BinaryObject
from .types import read_aamp_type, get_type_name
from .names import getName

class Node(BinaryObject):
    """AAMP node."""
    _reader = StructReader(
        ('I', 'node_id'),
        ('H', 'data_offset'),
        ('B', 'num_children'),
        ('B', 'data_type'),
    )

    def __init__(self, file=None):
        """Create new Node.

        file: File to read it from. (optional)
        """
        self.children = []
        self.data     = None
        if file is not None: self.readFromFile(file)


    def readFromFile(self, file):
        """Read the node from the given file."""
        super().readFromFile(file)

        curPos = file.tell()
        offset = (self.data_offset * 4) - self._reader._dataSize
        file.seek(offset, 1)

        if self.num_children > 0:
            for i in range(self.num_children):
                self.children.append(Node(file))
        else:
            self.data = read_aamp_type(file, self.data_type)

        file.seek(curPos) # restore position
        self.name = getName(self.node_id)


    def toXML(self, _depth=0):
        """Return XML string for this node."""
        pad = ' ' * _depth

        # XXX use proper XML module here...
        if self.num_children > 0:
            res = ['%s<%s>\n' % (pad, self.name)]
            for child in self.children:
                res.append(child.toXML(_depth=_depth+1))
            res.append('%s</%s>\n' % (pad, self.name))
            return ''.join(res)

        else:
            typ = get_type_name(self.data_type)
            return '%s<%s type="%s">%s</%s>\n' % (
                pad, self.name, typ, str(self.data), self.name)
