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

import io

class Encoder:
    """Base class for encoders.

    These represent a container for objects, and present an interface
    to pack those objects into a file.

    For plain binary files, the contents are one object, a byte stream.
    For archive files, the contents may be multiple objects.
    """

    def __init__(self, dest=None):
        """Create new encoder.

        dest: Path to output file.
        """
        self.dest = dest

    def pack(self, output:io.BufferedIOBase):
        """Encode this file.

        output: The output file (io.BufferedIOBase).
        """
        raise NotImplementedError
