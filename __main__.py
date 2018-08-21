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
import argparse
from app import App
import codec

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

    parser.add_argument('--list-recursive', '-L', nargs=1,
        action='append', metavar='PATH', default=[],
        help="List contents of file recursively.")

    parser.add_argument('--list-codecs', action='store_true',
        help="List supported file formats.")

    parser.add_argument('--license', action='store_true',
        help="Print this program's license.")

    parser.add_argument('--debug', action='store_true',
        help="Print debug messages.")

    return parser.parse_args()


def main():
    global arg_parser
    args = _setupArgs()
    if not any(vars(args).values()): # no argument given
        arg_parser.print_help()
        return 0

    if not args.debug: log.setLevel(logger.logging.INFO)
    if args.license: print(LICENSE)
    app = App()

    if args.list_codecs: app.list_codecs()
    dry = args.dry_run
    if dry: log.info("Dry run; not writing any files!")
    for arg in args.list: app.list_file(*arg)
    for arg in args.list_recursive: app.list_file_recursive(*arg)
    for arg in args.extract: app.extract_file(*arg, dry=dry)
    for arg in args.extract_recursive: app.extract_recursive(*arg, dry=dry)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except codec.UnsupportedFileTypeError as ex:
        sys.stderr.write(str(ex))
