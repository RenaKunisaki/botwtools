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
