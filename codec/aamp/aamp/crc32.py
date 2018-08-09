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

# I'm sure there's a built-in module for this, but I could only find
# binascii which doesn't seem to give the same results,
# probably because the initial poly is different?

def genTable():
    """Generate CRC32 table."""
    poly = 0xEDB88320
    temp = 0
    for i in range(256):
        temp = i
        for j in range(8, 0, -1):
            if (temp & 1) == 1:
                temp = ((temp >> 1) ^ poly) & 0xFFFFFFFF
            else: temp >>= 1
        yield temp
crc_table = list(genTable())


def crc32(data):
    """Compute CRC32 of data (bytes or str)."""
    if type(data) is str: data = bytes(data, 'utf-8')
    crc = 0xFFFFFFFF
    for b in data:
        i = (crc & 0xFF) ^ b
        crc = (crc >> 8) ^ crc_table[i]
    return (~crc) & 0xFFFFFFFF
