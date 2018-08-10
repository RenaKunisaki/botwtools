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
import os
import sys
import codec
import shutil
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

    parser.add_argument('--extract-recursive', '-X', nargs=2,
        action='append', metavar=('PATH', 'DESTPATH'), default=[],
        help="Extract file recursively (ie extract the extracted file).")

    parser.add_argument('--list', '-l', nargs=1, action='append',
        metavar='PATH', default=[],
        help="List contents of file.")

    parser.add_argument('--list-codecs', action='store_true',
        help="List supported file formats.")

    parser.add_argument('--license', action='store_true',
        help="Print this program's license.")

    return parser.parse_args()


def list_codecs():
    print("Available encoders:", ', '.join(sorted(set(
        map(lambda c: c.__codec_name__,
        codec.encoders.values()
    )))))
    print("Available decoders:", ', '.join(sorted(set(
        map(lambda c: c.__codec_name__,
        codec.decoders.values()
    )))))


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


def extract_directory(path):
    for name in map(lambda n: path+'/'+n, os.listdir(path)):
        if os.path.isdir(name):
            log.info("Recursing into %s", name)
            extract_directory(name)
        else:
            extract_recursive(name, name+'.tmp')
            os.remove(name)
            os.rename(name+'.tmp', name)


def extract_recursive(path, dest):
    log.info("Recursively extracting %s to %s...", path, dest)
    try:
        with open(path, 'rb') as file:
            decoder = codec.getDecoderForFile(file)
            decoder = decoder(file, dest)
            decoder.unpack()
        try: os.remove(dest+'.tmp')
        except IsADirectoryError: shutil.rmtree(dest+'.tmp')
        except FileNotFoundError: pass
        os.rename(dest, dest+'.tmp')
        extract_recursive(dest+'.tmp', dest)
    except IsADirectoryError:
        log.info("Recursing into %s", path)
        extract_directory(path)
    except codec.UnsupportedFileTypeError:
        log.info("Can't extract %s any further", path)
    finally:
        try: os.rename(dest+'.tmp', dest)
        except FileNotFoundError: pass


def main():
    global arg_parser
    args = _setupArgs()
    if not any(vars(args).values()):
        arg_parser.print_help()
        return 0

    if args.license: print(LICENSE)
    if args.list_codecs: list_codecs()
    for arg in args.list: list_file(arg)
    for arg in args.extract: extract_file(*arg)
    for arg in args.extract_recursive: extract_recursive(*arg)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except codec.UnsupportedFileTypeError as ex:
        sys.stderr.write(str(ex))
