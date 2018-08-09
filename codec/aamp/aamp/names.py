import os
dir_path = os.path.dirname(os.path.realpath(__file__))

import logging; log = logging.getLogger()
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
