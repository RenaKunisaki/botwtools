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

import logging; log = logging.getLogger()
import io
import os
import sys
from .types import Path, BinInput, BinOutput, TxtOutput, fopenMode

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
    #__codec_name__ = 'your decoder should put a name here'
    defaultFileExt = 'extracted'

    def __init__(self, input:BinInput, output:Path=None):
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

    @classmethod
    def suggestOutputName(cls, path:Path) -> Path:
        """Given the path of the input file,
        suggest a path for the output file.
        """
        #path, ext = os.path.splitext(path)
        return path + '.' + cls.defaultFileExt

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
        if path == '': path = '.' # don't extract archives to /
        log.debug("mkfile name=%s, path=%s (dest=%s)", name, path,
            self.destPath)
        if path != '':
            path = self.mkdir(path) + '/'
        return open(path+name, mode)

    def writeFile(self, path:Path, data):
        """Write data to a file within the output directory."""
        with self.mkfile(path) as file:
            file.write(data)
