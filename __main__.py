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
import io
import os
import sys
import codec
import shutil
import argparse
import tempfile
from filereader import FileReader
from filewriter import FileWriter

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


def _format_size(size):
    units = ' KMG'
    unit  = 0
    while(size > 9999 and unit < len(units)):
        size /= 1024
        unit += 1
    return '%4d%s' % (size, units[unit])


def get_files(obj, name, _depth=0):
    """Recursively get all files in given object.

    Returns list of files.
    """
    #log.debug("listing %s", obj)
    items = []
    name = getattr(obj, 'name', name)
    if hasattr(obj, 'defaultFileExt'):
        name += '.' + obj.defaultFileExt

    if hasattr(obj, 'toData'):
        log.debug("recursing into %s, name=%s", obj, name)
        file = tempfile.TemporaryFile()
        file.write(obj.toData())
        file.seek(0, 0)
        file = FileReader(file)
        try:
            decoder = codec.getDecoderForFile(file)
        except codec.UnsupportedFileTypeError:
            log.debug("can't decode %s", obj)
            return [{'name':name, 'obj':obj, 'file':file}]

        decoder = decoder(file, None)
        items += get_files(decoder, name, _depth+1)
        #for item in decoder.objects:
        #    items += get_files(item, _depth+1)
        if len(items) == 0:
            items = [{'name':name, 'obj':obj, 'file':file}]
        log.debug("%s => %s", obj, items)
    else:
        if not getattr(obj, 'isListable', False):
            log.debug("Can't list object: %s", obj)
            return items

        log.debug("no data in %s", obj)
        for item in getattr(obj, 'objects', []):
            items += get_files(item, _depth+1)
        log.debug("%s => %s", obj, items)
    return items


def list_file(path):
    """Print list of given file's contents."""
    with FileReader(path, 'rb') as file:
        decoder = codec.getDecoderForFile(file)
        decoder = decoder(file, None)
        decoder.printList()


def _list_recursive(obj, _depth=0):
    ind = '  ' * _depth

    if not getattr(obj, 'isListable', False):
        #log.debug("Can't list object: %s", obj)
        return
    #else:
    #    log.debug("Listing object: %s", obj)

    try: name = obj.toString()
    except AttributeError: name = str(obj)

    try: print('%s[%s] %s' % (ind, _format_size(obj.size), name))
    except AttributeError: print('%s%s' % (ind, name))


    with tempfile.TemporaryFile() as file:
        try:
            file.write(obj.toData())
        except AttributeError:
            return
        file.seek(0, 0)
        file = FileReader(file)
        try:
            decoder = codec.getDecoderForFile(file)
        except codec.UnsupportedFileTypeError:
            return
        decoder = decoder(file, None)
        for item in decoder.objects:
            _list_recursive(item, _depth+1)


def extract_recursive(path, dest, dry=False):
    with FileReader(path, 'rb') as file:
        decoder = codec.getDecoderForFile(file)
        decoder = decoder(file, None)
        items   = get_files(decoder, path)
        for item in items:
            log.info("Extracting %s/%s...", dest, item['name'])
            if not dry:
                with FileWriter(dest+'/'+item['name']) as output:
                    if 'file' in item:
                        item['file'].seek(0)
                        output.write(item['file'].read())
                    else:
                        output.write(item['obj'].toData())


def list_file_recursive(path):
    """Print list of given file's contents recursively."""
    with FileReader(path, 'rb') as file:
        decoder = codec.getDecoderForFile(file)
        decoder = decoder(file, None)
        items   = []
        for obj in decoder.objects:
            _list_recursive(obj)


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
    if dry: log.info("Dry run; not writing any files!")
    for arg in args.list: list_file(*arg)
    for arg in args.list_recursive: list_file_recursive(*arg)
    for arg in args.extract: extract_file(*arg, dry=dry)
    for arg in args.extract_recursive: extract_recursive(*arg, dry=dry)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except codec.UnsupportedFileTypeError as ex:
        sys.stderr.write(str(ex))
