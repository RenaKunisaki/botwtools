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
import codec

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
        self._offset    = 0

    def read(self, size=-1, offset=None):
        """Read bytes from the file."""
        if offset is not None: self.seek(offset)
        offset = self._offset
        if size < 0: size = self.size - offset
        if offset >= self.size: return b''
        src = self.archive.file
        src.seek(self.data_start + self.archive.header.data_offset + offset)
        self._offset += size
        return src.read(size)

    def seek(self, pos, whence=0):
        if whence in (0, 'start'): self._offset = pos
        elif whence in (1, 'cur'): self._offset += pos
        elif whence in (2, 'end'): self._offset = self.size - pos
        else: raise ValueError("Invalid whence")

        if self._offset < 0: self._offset = 0
        if self._offset > self.size: self._offset = self.size
        # offset can == size, meaning we return EOF

    def tell(self):
        return self._offset

    def toData(self):
        return self.read()

    def toString(self):
        """Return pretty string describing this object."""
        try:
            typ = codec.getDecoderForFile(self).__codec_name__
        except:
            typ = '<unknown type>'
        return '%s file "%s"' % (typ, self.name)

    def __str__(self):
        return "<File:%s at 0x%x>" % (self.name, id(self))
