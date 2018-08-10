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


# Ackowledgememts
Uses third-party libraries:
    - libyaz0 by MasterVermilli0n / AboodXD
    - byml-v2 by leoetlino <leo@leolam.fr>


# Bugs/Limitations
- Currently does not support little-endian (WiiU) SARC files.
- Does not handle AAMP files with multiple roots.
- This program is only tested on Linux, but probably works fine on Windows too.
- This program only operates on files extracted from the game image. It cannot unpack the `.xci` image file. Use `nxtools` for that. I will not help you obtain the game image/files.
