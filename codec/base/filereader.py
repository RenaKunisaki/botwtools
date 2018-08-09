import io

class FileReader:
    """Helper class for reading binary files."""
    def __init__(self, file):
        self.file = file

    def seek(self, pos, whence=0):
        self.file.seek(pos, whence)

    def read(self, size=-1, pos=None):
        if pos is not None: self.seek(pos)
        return self.file.read(size)

    def readString(self, pos=None, maxlen=None, encoding='shift-jis'):
        """Read null-terminated string from file."""
        if pos is not None: self.seek(pos)
        s = []
        while maxlen == None or len(s) < maxlen:
            b = self.file.read(1)
            if b == b'\0': break
            else: s.append(b)

        s = b''.join(s)
        if encoding is not None: s = s.decode()
        return s
