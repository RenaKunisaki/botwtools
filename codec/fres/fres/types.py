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

def unpack10bit(val):
    # XXX sign bit
    if type(val) in (list, tuple):
        val = val[0] # grumble grumble struct is butts
    v0 = ( val        & 0x3FF) / 511
    v1 = ((val >> 10) & 0x3FF) / 511
    v2 = ((val >> 20) & 0x3FF) / 511
    return v0, v1, v2

# attribute format ID => struct fmt
attrFmts = {
    0x0201: {
        'fmt':          'B',
        'collada_type': 'int',
        'min': 0, 'max':255,
    },
    0x0901: {
        'fmt':          '2B',
        'collada_type': 'int',
        'min': 0, 'max':255,
    },
    0x0B01: {
        'fmt':          '4B',
        'collada_type': 'int',
        'min': 0, 'max':255,
    },
    0x1201: {
        'fmt':          '2H',
        'collada_type': 'int',
        'min': 0, 'max':65535,
    },
    0x1501: {
        'fmt':          '2h',
        'collada_type': 'int',
        'min': -32768, 'max':32767,
    },
    0x1701: {
        'fmt':          '2i',
        'collada_type': 'int',
        min: -0x80000000, max: 0x7FFFFFFF,
    },
    0x1801: {
        'fmt':          '3i',
        'collada_type': 'int',
        min: -0x80000000, max: 0x7FFFFFFF,
    },
    0x0B02: {
        'fmt':          '4B',
        'collada_type': 'int',
        'min': 0, 'max':255,
    },
    0x0E02: {
        'fmt':          'I',
        'collada_type': 'float',
        'func':         unpack10bit,
    },
    0x1202: {
        'fmt':          '2h',
        'collada_type': 'int',
        'min': -32768, 'max':32767,
    },
    0x0203: {
        'fmt':          'B',
        'collada_type': 'int',
        'min': 0, 'max':255,
    },
    0x0903: {
        'fmt':          '2B',
        'collada_type': 'int',
        'min': 0, 'max':255,
    },
    0x0B03: {
        'fmt':          '4B',
        'collada_type': 'int',
        'min': 0, 'max':255,
    },
    0x1205: {
        'fmt':          '2e',   # half float
        'collada_type': 'float',
    },
    0x1505: {
        'fmt':          '4e',
        'collada_type': 'float',
    },
    0x1705: {
        'fmt':          '2f',
        'collada_type': 'float',
    },
    0x1805: {
        'fmt':          '3f',
        'collada_type': 'float',
    },
}
