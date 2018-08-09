#!/usr/bin/env python3
# This file is part of botwtools.
LICENSE = """
botwtools is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

botwtools is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with botwtools.  If not, see <https://www.gnu.org/licenses/>.
"""

import logger; logger.setup('botwtools')
log = logger.logging.getLogger()
import sys
import codec
import argparse

arg_parser = None

def _setupArgs():
    global arg_parser
    parser = argparse.ArgumentParser(
        description="Breath of the Wild modding tools.")
    arg_parser = parser

    parser.add_argument('--extract', '-x', nargs=2, action='append',
        metavar=('PATH', 'DESTPATH'), default=[],
        help="Extract file to specified path.")

    parser.add_argument('--list', '-l', nargs=1, action='append',
        metavar='PATH', default=[],
        help="List contents of file.")

    parser.add_argument('--list-codecs', action='store_true',
        help="List supported file formats.")

    parser.add_argument('--license', action='store_true',
        help="Print this program's license.")

    return parser.parse_args()


def list_codecs():
    print("Available encoders:", ', '.join(map(
        lambda f: f.decode('utf-8'),
        sorted(codec.encoders.keys())
    )))
    print("Available decoders:", ', '.join(map(
        lambda f: f.decode('utf-8'),
        sorted(codec.decoders.keys())
    )))


def list_file(path):
    with open(path, 'rb') as file:
        decoder = codec.getDecoderForFile(file)
        decoder = decoder(file, None)
        decoder.printList()


def extract_file(path, dest):
    log.info("Extracting %s...", path)
    with open(path, 'rb') as file:
        decoder = codec.getDecoderForFile(file)
        decoder = decoder(file, dest)
        decoder.unpack()


def main(*args):
    global arg_parser
    args = _setupArgs()
    if not any(vars(args).values()):
        arg_parser.print_help()
        return 0

    if args.license: print(LICENSE)
    if args.list_codecs: list_codecs()
    for arg in args.list: list_file(arg)
    for arg in args.extract: extract_file(*arg)

    # XXX recursive extraction: try to extract each extracted file,
    # until we find one we don't support.
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(*sys.argv[1:]))
    except codec.UnsupportedFileTypeError as ex:
        sys.stderr.write(str(ex))
