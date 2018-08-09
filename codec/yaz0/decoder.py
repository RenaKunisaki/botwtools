# This is basically a tidied-up version of libyaz0 by
# MasterVermilli0n / AboodXD.
# Licensed under GPLv3.

# Yaz0 is a compressed format based on LZ, used in many Nintendo games.
# It's the successor to MIO0/YAY0 used in N64 games.
# Technically, `Yaz` is the file marker, and the 0 (or 1) tells if it comes
# from the original media or an expansion disk. Yaz1 is identical to Yaz0
# and is rarely seen.
import logging; log = logging.getLogger()
import io
import struct
from ..base import Decoder, FileReader, UnsupportedFileTypeError

class Yaz0Stream(io.RawIOBase):
    """Yaz0 byte stream.

    Accepts an input file and yields bytes of the decompressed data.
    """
    def __init__(self, file):
        self.file = FileReader(file)
        self.magic, self.dest_end = struct.unpack('>4sI', self.file.read(8))
        if self.magic not in (b'Yaz0', b'Yaz1'):
            raise UnsupportedFileTypeError(self.magic)
        self.src_pos  = 16
        self.dest_pos = 0
        self._output  = []

    def _nextByte(self):
        d = self.file.read(1, self.src_pos)[0]
        self.src_pos += 1
        return d

    def _outputByte(self, b):
        if type(b) is int: b = bytes((b,))
        self._output.append(b)
        self.dest_pos += 1
        return b

    def bytes(self):
        """Generator that yields bytes from the decompressed stream."""
        code     = 0
        code_len = 0
        while self.dest_pos < self.dest_end:
            if not code_len:
                code = self._nextByte()
                code_len = 8
            if code & 0x80:
                yield self._outputByte(self._nextByte())
            else:
                b1 = self._nextByte()
                b2 = self._nextByte()
                offs = ((b1 & 0x0F) << 8) | b2
                copy_src = self.dest_pos - (offs & 0xFFF) - 1
                n = b1 >> 4
                if n: n += 2
                else: n = self._nextByte() + 0x12
                assert (3 <= n <= 0x111)
                for i in range(n):
                    yield self._outputByte(self._output[copy_src])
                    copy_src += 1
            code <<= 1
            code_len -= 1

    def read(self, size=-1):
        """File-like interface for reading decompressed stream."""
        res = []
        data = self.bytes()
        while size < 0 or len(res) < size:
            try: res.append(next(data))
            except StopIteration: break
        return b''.join(res)

    def __str__(self):
        return "<Yaz0 stream at 0x%x>" % id(self)


class Yaz0Decoder(Decoder):
    """Decoder for Yaz0-compressed files."""

    def _read(self):
        self.stream = Yaz0Stream(self.input)

    def _iter_objects(self):
        yield self.stream # only one object

    def unpack(self):
        with open(self.destPath, 'wb') as file:
            file.write(self.stream.read())
