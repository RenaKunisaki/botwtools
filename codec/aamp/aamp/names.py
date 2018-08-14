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

import os
dir_path = os.path.dirname(os.path.realpath(__file__))

import logging; log = logging.getLogger(__name__)
from .crc32 import crc32

# keep a log of all unknown hashes.
# eventually we can try to brute force them.
unknown_hashes = {}
with open(dir_path+'/unknown-hashes.txt') as file:
    for line in file:
        unknown_hashes[int(line.strip())] = True

def log_unknown_hash(hash):
    """If a hash is unknown, add to the list of unknown hashes."""
    if hash not in unknown_hashes:
        log.warn("New unknown hash %08X", hash)
        unknown_hashes[hash] = True
        with open(dir_path+'/unknown-hashes.txt', 'a') as file:
            file.write('%d\n' % hash)


# read the known hashes
name_hashes = {}
with open(dir_path+'/names.txt') as file:
    for line in file:
        line = line.strip()
        hash = crc32(line)
        if hash in name_hashes and name_hashes[hash] != line:
            log.warn("duplicate hash %s:\n  %s\n  %s", hash,
                name_hashes[hash], line)
        name_hashes[hash] = line
    log.debug("computed %d name hashes", len(name_hashes))


def getName(hash):
    """Look up the name for a hash."""
    try:
        return name_hashes[hash]
    except KeyError:
        log_unknown_hash(hash)
        return 'unknown_%08X' % hash
