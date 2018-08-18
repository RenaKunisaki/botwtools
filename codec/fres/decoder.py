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

# FRES decoding is a bit ugly because an FRES is an archive, but many
# of its contents are not simple files, but structs which point to
# various locations in the FRES file. So we can't simply extract all
# the files and decode them separately; we need to decode to extract.

import logging; log = logging.getLogger(__name__)
import io
import sys
import struct
from filereader import FileReader
from ..base import ArchiveDecoder, UnsupportedFileTypeError, TxtOutput
from ..base.types import Path, BinInput, BinOutput, TxtOutput, fopenMode
from .fres import FRES


class FresDecoder(ArchiveDecoder):
    """Decoder for FRES archive."""
    __codec_name__ = 'FRES'

    def _read(self):
        """Read the input file, upon opening it."""
        self.archive = FRES().readFromFile(self.input)
        log.debug("FRES contains %d models",
            len(self.archive.fmdls))


    def _iter_objects(self):
        """Iterate over the objects in this file."""
        objs = (list(self.archive.fmdls) +
            list(self.archive.embeds)
            # XXX + others...
            )
        return objs


    def _get_num_objects(self) -> (int, None):
        """Get number of objects in this file.

        Returns None if not known.
        """
        return (self.archive.header.fmdl_cnt +
            self.archive.header.fska_cnt +
            self.archive.header.fmaa_cnt +
            self.archive.header.fvis_cnt +
            self.archive.header.fshu_cnt +
            self.archive.header.fscn_cnt +
            self.archive.header.embed_cnt)


    def printList(self, dest:TxtOutput=sys.stdout):
        """Print nicely formatted list of this file's objects."""
        objs = []
        for typ in self.archive.object_types:
            name, cls = typ
            objs += self.archive.getObjects(name)
        print("%d objects" % len(objs))
        for i, obj in enumerate(objs):
            print('  %3d: %s: "%s"' % (i, type(obj).__name__, obj.name))

    def _extractTexture(self, texture, name):
        """Export texture to BNTX file."""
        self.archive.file.seek(texture['offset'])
        data = self.archive.file.read(texture['size'])
        self.writeFile(name, data)
