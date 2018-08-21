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
import io
import os
import struct
from lxml import etree as ET
from filereader import FileReader
from ..base import Decoder, UnsupportedFileTypeError, BinInput
from .aamp import Header, Node, RootNode

class AampDecoder(Decoder):
    """Decoder for AAMP files."""
    __codec_name__ = 'AAMP'
    defaultFileExt = 'xml'
    
    def _read(self):
        """Read the input file, upon opening it."""
        self.header = Header().readFromFile(self.input)
        self._validateFileSize()
        self.roots = []
        for i in range(self.header.num_root_nodes):
            self.input.seek(0x34 + (i*RootNode._reader.size))
            self.roots.append(RootNode(self.input))

    def _validateFileSize(self):
        """Make sure file size matches what header says it is."""
        try:
            pos  = self.input.tell()
            size = self.input.seek(0, 2)
            self.input.seek(pos, 0) # return to original position
            if self.header.filesize != size:
                log.warn("AAMP header says filesize is %d, "
                    "but it's actually %d",
                    self.header.filesize, size)
                return False
        except io.UnsupportedOperation:
            # can't seek; this is probably stdin or such
            pass
        return True

    def _iter_objects(self):
        """Iterate over the objects in this file."""
        return self.roots

    def _get_num_objects(self) -> (int, None):
        """Get number of objects in this file.

        Returns None if not known.
        """
        return self.header.num_root_nodes

    def unpack(self):
        """Unpack this file to `self.destPath`."""
        ns    = '{'+self.roots[0].xmlns+'}'
        root  = ET.Element('aamp', nsmap=self.roots[0].xmlnsmap)
        for r in self.roots: root.append(r.toXML())

        # decode and escape the null byte
        str_xml = (self.header.str_xml.decode('utf-8')
            .replace('\0', '\\0'))

        attrs = {
            'version':       self.header.version,
            'unk08':         self.header.unk08,
            'filesize':      self.header.filesize,
            'unk10':         self.header.unk10,
            'unk2C':         self.header.unk2C,
            'str_xml':       str_xml,
            'data_buf_size': self.header.data_buf_size,
            'str_buf_size':  self.header.str_buf_size,
        }
        for k, v in attrs.items():
            root.set(ns+k, str(v))

        with open(self.destPath, 'wb') as file:
            tree = ET.ElementTree(root)
            tree.write(file,
                encoding='utf-8',
                xml_declaration=True,
                pretty_print=True,
            )
