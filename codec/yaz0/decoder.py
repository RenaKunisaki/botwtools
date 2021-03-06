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

# This is basically a tidied-up version of libyaz0 by
# MasterVermilli0n / AboodXD, whch is also GPLv3.

# Yaz0 is a compressed format based on LZ, used in many Nintendo games.
# It's the successor to MIO0/YAY0 used in N64 games.
# Technically, `Yaz` is the file marker, and the 0 (or 1) tells if it
# comes from the original media or an expansion disk.
# Yaz1 is identical to Yaz0 and is rarely seen.
import logging; log = logging.getLogger(__name__)
import io
import os
import struct
from ..base import Decoder, UnsupportedFileTypeError, BinInput

class Yaz0Stream(io.RawIOBase):
    """Yaz0 byte stream.

    Accepts an input file and yields bytes of the decompressed data.
    """
    isListable = True # `--list-recursive` should enumerate this

    def __init__(self, file:BinInput):
        self.file = file
        # temp files' names can be integers, not strings
        _, name = os.path.split(str(file.name))
        self.name = name + '.out'
        self.magic, self.dest_end = self.file.read('>4sI')
        if self.magic not in (b'Yaz0', b'Yaz1'):
            raise UnsupportedFileTypeError(self.magic)
        self.src_pos  = 16
        self.dest_pos = 0
        self.size     = self.dest_end
        self._output  = []
        self._outputStart = 0
        log.debug("Yaz0 output size: %d", self.size)


    def _nextByte(self) -> bytes:
        """Return next byte from input, or EOF."""
        d = self.file.read(1, self.src_pos)[0]
        self.src_pos += 1
        return d


    def _outputByte(self, b:(int,bytes)) -> bytes:
        """Write byte to output and return it."""
        if type(b) is int: b = bytes((b,))
        self._output.append(b)

        # we only need to keep the last 0x1111 bytes of the output
        # since that's the furthest back we can seek to copy from.
        excess = len(self._output) - 0x1111
        if excess > 0:
            self._output = self._output[-0x1111:]
            self._outputStart += excess

        self.dest_pos += 1
        if self.dest_pos & 0x1FFFF == 0:
            log.debug("extracted: %d / %dK %d%%",
                self.dest_pos / 1024,
                self.size / 1024,
                (self.dest_pos / self.size) * 100)
        return b


    def bytes(self):
        """Generator that yields bytes from the decompressed stream."""
        code     = 0
        code_len = 0
        while self.dest_pos < self.dest_end:
            if not code_len:
                code = self._nextByte()
                code_len = 8
            if code & 0x80: # output next byte from input
                yield self._outputByte(self._nextByte())
            else: # repeat some bytes from output
                b1 = self._nextByte()
                b2 = self._nextByte()
                offs = ((b1 & 0x0F) << 8) | b2
                copy_src = self.dest_pos - (offs & 0xFFF) - 1
                n = b1 >> 4
                if n: n += 2
                else: n = self._nextByte() + 0x12
                assert (3 <= n <= 0x111)
                for i in range(n):
                    #log.debug("copy src=0x%X start=0x%X len=0x%X",
                    #    copy_src, self._outputStart, len(self._output))
                    p = copy_src - self._outputStart
                    yield self._outputByte(self._output[p])
                    copy_src += 1
            code <<= 1
            code_len -= 1


    def read(self, size:int=-1) -> bytes:
        """File-like interface for reading decompressed stream."""
        res = []
        data = self.bytes()
        while size < 0 or len(res) < size:
            try: res.append(next(data))
            except StopIteration: break
        return b''.join(res)


    def toData(self):
        """Return the object in a form that can be written to a file."""
        return self.read()


    def toString(self):
        """Return pretty string describing this object."""
        return 'Yaz0-compressed file "%s"' % self.file.name


    def __str__(self):
        return "<Yaz0 stream at 0x%x>" % id(self)



class Yaz0Decoder(Decoder):
    """Decoder for Yaz0-compressed files."""
    __codec_name__ = 'Yaz0'

    def _read(self):
        """Read the input file, upon opening it."""
        self.stream = Yaz0Stream(self.input)

    def _iter_objects(self):
        """Iterate over the objects in this file."""
        # Yaz0 is a single-file compression format,
        # so we only contain one object, which is
        # the compressed data stream.
        yield self.stream
