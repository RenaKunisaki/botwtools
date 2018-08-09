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

class UnsupportedFileTypeError(RuntimeError):
    """Raised when trying to operate on a file type we don't support."""
    def __init__(self, typ):
        self.fileType = typ
        super().__init__("Unsupported file type: %s (magic=0x%08X)" % (
            str(typ), struct.unpack('I', typ)[0]))
