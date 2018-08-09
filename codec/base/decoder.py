import logging; log = logging.getLogger()
import io
import os
import sys

# some type annotations
Path      = str
BinInput  = io.BufferedIOBase
BinOutput = io.BufferedIOBase
TxtOutput = io.TextIOBase
fopenMode = str

class Decoder:
    """Base class for decoders.

    These represent an input file which contains zero or more
    objects. The class presents an interface to enumerate and
    extract the file contents.

    For plain binary files, the contents are one object, which is
    a byte stream representing the raw data.
    For archive files, the contents are zero or more objects,
    such as files.
    """

    def __init__(self, input:BinInput, output:BinOutput=None):
        """Create new decoder.

        input: File to decode.
        output: Destination path. Can be excluded if not extracting files.
        """
        self.input    = input
        self.destPath = output
        self._read()

    def _read(self):
        """Read the input file, upon opening it."""
        raise NotImplementedError

    @property
    def objects(self):
        """An iterator over the objects in the file.

        Decoders should implement `_iter_objects` instead.
        """
        return self._iter_objects()

    @property
    def numObjects(self):
        """Number of objects in this file.

        Decoders should implement `_get_num_objects` instead.
        """
        # This is a property rather than using len(objects)
        # because objects might be a generator, to which
        # len() can't apply. Otherwise, we might need to
        # decode the entire file just to count the objects.
        # This method can return None if the number isn't known.
        return self._get_num_objects()

    def _iter_objects(self):
        """Iterate over the objects in this file."""
        raise NotImplementedError

    def _get_num_objects(self) -> (int, None):
        """Get number of objects in this file.

        Returns None if not known.
        """
        return None

    def printList(self, dest:TxtOutput=sys.stdout):
        """Print nicely formatted list of this file's objects."""
        if self.numObjects is not None:
            print("Objects:", self.numObjects)
        for obj in self.objects:
            print(obj)

    def unpack(self):
        """Unpack this file to `self.destPath`."""
        raise NotImplementedError

    def mkdir(self, path:Path) -> Path:
        """Create a subdirectory within the output directory.

        Allows multiple nested paths (eg foo/bar/baz).
        Does nothing if the directory already exists.

        Returns the full, normalized path to the directory.
        """
        path = os.path.normpath(self.destPath + '/' + path)
        if path != '':
            dirs = path.split('/')
            for i in range(len(dirs)):
                p = '/'.join(dirs[0:i+1])
                try: os.mkdir(p)
                except FileExistsError: pass
        return path

    def mkfile(self, path:Path, mode:fopenMode='wb') -> BinOutput:
        """Create a file within the output directory.

        Allows multiple nested paths. Creates the directories as needed.

        Returns the file object.
        """
        path, name = os.path.split(path)
        log.debug("mkfile name=%s, path=%s", name, path)
        if path != '': path = self.mkdir(path)
        return open(path+'/'+name, mode)

    def writeFile(self, path:Path, data):
        """Write data to a file within the output directory."""
        with self.mkfile(path) as file:
            file.write(data)
