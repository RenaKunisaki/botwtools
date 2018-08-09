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
