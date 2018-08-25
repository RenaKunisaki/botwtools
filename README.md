Breath of the Wild modding tools
by Rena Kunisaki - `('moc.liamg@rekcahrepyh'):reverse()`

# Description
A program to extract several file types found in BotW (and maybe other games). Eventually, will be able to repack them too. Designed in such a way that it should hopefully be simple enough to add your own file types.


# Usage
Run `python botwtools` or `./botwtools/__main__.py` and follow instructions.


# Requirements
Requires Python 3 and modules:

- PyYAML
- sortedcontainers


# Acknowledgememts
Uses third-party libraries:

- libyaz0 by MasterVermilli0n / AboodXD
- byml-v2 by leoetlino <leo@leolam.fr>
- BnTxx by gdkchan
- PNG writing code by Guido U. Draheim

Thanks to leoetlino and KillzXGaming for help reverse engineering file formats.


# Bugs/Limitations
- Currently does not support little-endian (WiiU) SARC files.
- Since AAMP only stores the hashes of element names, many elements come out named `unknown_xxxxxxxx`.
    - I've brute-forced a handful of hashes, but CRC32 is prone to collisions, so some of the names might be nonsense that happens to have the same hash.
- Recursive extraction might be buggy.
- Exported models' textures might not be assigned to the correct UV maps and attributes.
    - In particular, the normal-map textures seem to be missing entirely, and the specular textures are applied to color instead of intensity. These might be Blender bugs because I have no idea.
- This program is only tested on Linux, but probably works fine on Windows too.
- This program only operates on files extracted from the game image. It cannot unpack the `.xci` image file. Use `nxtools` for that. I will not help you obtain the game image/files.
