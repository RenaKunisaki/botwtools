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
#
# This file also contains code from byml-v2 which is
# published under the GPLv2+ license.

import logging; log = logging.getLogger(__name__)
import io
import os
import struct
import yaml
from ..base import Decoder, UnsupportedFileTypeError, BinInput
from . import byml

def byml_to_yml(root) -> None:
    # taken from byml-v2 by leoetlino
    # Licensed under GPLv2+
    dumper = yaml.CDumper
    types = {
        'Int':   lambda d,v: d.represent_int(v),
        'Float': lambda d,v: d.represent_float(v),
        'UInt':  lambda d,v: d.represent_scalar(u'!u',   '0x%08x'%v),
        'Int64': lambda d,v: d.represent_scalar(u'!l',   str(v)),
        'UInt64':lambda d,v: d.represent_scalar(u'!ul',  str(v)),
        'Double':lambda d,v: d.represent_scalar(u'!f64', str(v)),
    }
    for k, v in types.items():
        yaml.add_representer(getattr(byml, k), v, Dumper=dumper)

    output = io.StringIO()
    yaml.dump(root, output,
        Dumper=dumper, allow_unicode=True, encoding='utf-8')
    return output.getvalue()


class RootNode:
    isListable = False
    defaultFileExt = 'yaml'

    def __init__(self, name, data):
        self.name = name
        self.byml = byml.Byml(data)
        self.root = self.byml.parse()

    def toData(self):
        return byml_to_yml(self.root)


class BymlDecoder(Decoder):
    """Decoder for BYML files."""
    __codec_name__ = 'BYML'
    defaultFileExt = 'yaml'

    def _read(self):
        """Read the input file, upon opening it."""
        self.root = RootNode(self.input.name, self.input.read())

    def _iter_objects(self):
        """Iterate over the objects in this file."""
        yield self.root
