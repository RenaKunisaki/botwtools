import struct

class UnsupportedFileTypeError(RuntimeError):
    """Raised when trying to operate on a file type we don't support."""
    def __init__(self, typ):
        self.fileType = typ
        super().__init__("Unsupported file type: %s (magic=0x%08X)" % (
            str(typ), struct.unpack('I', typ)[0]))
