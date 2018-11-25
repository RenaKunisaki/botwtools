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

import logging; log = logging.getLogger(__name__)

class Buffer:
    """A buffer of data that can be read in various formats."""

    def __init__(self, file, size, stride, offset):
        self.file   = file
        self.size   = size
        self.stride = stride
        self.offset = offset
        self.data   = file.read(size, offset)
        if len(self.data) < size:
            log.warn("Buffer size is 0x%X but only read 0x%X",
                size, len(self.data))

        log.debug("Buffer size=%04X stride=%04X offs=%06X: %s %s",
            size, stride, offset,
            ' '.join(map(lambda b: '%02X'%b, self.data[0:16])),
            self.data[0:16])

        fmts = {
              'int8': 'b',
             'uint8': 'B',
             'int16': 'h',
            'uint16': 'H',
            ' int32': 'i',
            'uint32': 'I',
            ' int64': 'q',
            'uint64': 'Q',
            #'half':   'e',
            'float':  'f',
            'double': 'd',
            'char':   'c',
        }
        for name, fmt in fmts.items():
            try:
                view = memoryview(self.data).cast(fmt)
                setattr(self, name, view)
            except TypeError:
                # this just means we can't interpret the buffer as
                # eg int64 because its size isn't a multiple of
                # that type's size.
                log.debug("FRES buffer: data size 0x%X doesn't fit format %s for type %s",
                    len(self.data), fmt, name)
