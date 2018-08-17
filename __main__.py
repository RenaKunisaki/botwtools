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
import tempfile
from filereader import FileReader

arg_parser = None # declare global

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

    parser.add_argument('--dry-run', action='store_true',
        help="Do not actually create any files.")

    parser.add_argument('--list', '-l', nargs=1, action='append',
        metavar='PATH', default=[],
        help="List contents of file.")

    parser.add_argument('--list-codecs', action='store_true',
        help="List supported file formats.")

    parser.add_argument('--license', action='store_true',
        help="Print this program's license.")

    parser.add_argument('--debug', action='store_true',
        help="Print debug messages.")

    return parser.parse_args()


def list_codecs():
    """Print list of available encoders and decoders."""
    print("Available encoders:", ', '.join(sorted(set(
        map(lambda c: c.__codec_name__,
        codec.encoders.values()
    )))))
    print("Available decoders:", ', '.join(sorted(set(
        map(lambda c: c.__codec_name__,
        codec.decoders.values()
    )))))


def list_file(path):
    """Print list of given file's contents."""
    with FileReader(path, 'rb') as file:
        decoder = codec.getDecoderForFile(file)
        decoder = decoder(file, None)
        decoder.printList()


def extract_file(path, dest, dry=False):
    """Extract given file to given destination."""
    log.info("Extracting %s...", path)
    with FileReader(path, 'rb') as file:
        decoder = codec.getDecoderForFile(file)
        decoder = decoder(file, dest, dry=dry)
        decoder.unpack()


def extract_directory(path, dry=False, _depth=0):
    """Recursively extract given directory.

    Called from extract_recursive.
    """
    log.info("Recursing into %s", path)
    for name in map(lambda n: path+'/'+n, os.listdir(path)):
        if os.path.isdir(name):
            extract_directory(name, dry=dry, _depth=_depth+1)
        else:
            extract_recursive(name, name, dry=dry, _depth=_depth+1)


def extract_recursive(path, dest, dry=False, _depth=0):
    """Recursively extract given file/directory to given destination."""
    log.info("Recursively extracting %s to %s...", path, dest)
    temp_path = tempfile.mkdtemp()
    try:
        # extract the input file
        with FileReader(path, 'rb') as file:
            decoder = codec.getDecoderForFile(file)
            #name    = os.path.normpath(decoder.suggestOutputName(dest))
            #log.debug("in(%s) sugg(%s) out(%s)", path, name, dest)
            # XXX on Windows we may not be able to open this file.
            log.debug("decoder(%s, %s)", file, temp_path)
            decoder = decoder(file, temp_path)
            decoder.unpack()

        # if successful, remove the input file, if we created it
        if _depth > 0:
            log.debug("Removing intermediate file %s", path)
            os.remove(path)

        # recurse into this file
        extract_recursive(temp_path, temp_path, dry=dry, _depth=_depth+1)

    except IsADirectoryError: # recurse into the directory
        extract_directory(path, dry=dry, _depth=_depth+1)

    except codec.UnsupportedFileTypeError:
        log.info("Can't extract %s any further", path)
        shutil.move(temp_path, dest)

    except FileNotFoundError:
        if _depth > 0:
            # we tried to recurse into the file we just created,
            # but there was no file. previous stage did nothing.
            log.warning("Nothing extracted from %s", path)
        else: # the user-supplied input file is missing.
            raise


def main():
    global arg_parser
    args = _setupArgs()
    if not any(vars(args).values()): # no argument given
        arg_parser.print_help()
        return 0

    if not args.debug: log.setLevel(logger.logging.INFO)
    if args.license: print(LICENSE)
    if args.list_codecs: list_codecs()
    dry = args.dry_run
    log.debug("dry=%s", dry)
    if dry: log.info("Dry run; not writing any files!")
    for arg in args.list: list_file(*arg)
    for arg in args.extract: extract_file(*arg, dry=dry)
    for arg in args.extract_recursive: extract_recursive(*arg, dry=dry)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except codec.UnsupportedFileTypeError as ex:
        sys.stderr.write(str(ex))
