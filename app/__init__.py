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

import logging; log = logging.getLogger(__name__)
import io
import os
import sys
import codec
import shutil
import tempfile
from filereader import FileReader
from filewriter import FileWriter


def _format_size(size):
    units = ' KMG'
    unit  = 0
    while(size > 9999 and unit < len(units)):
        size /= 1024
        unit += 1
    return '%4d%s' % (size, units[unit])


class App:
    """The main application."""

    def __init__(self):
        pass

    def _list_codecs(self, codecs):
        return ', '.join(sorted(set(
            map(lambda c: c.__codec_name__,
            codecs.values()
        ))))

    def list_codecs(self):
        """Print list of available encoders and decoders."""
        print("Available encoders:", self._list_codecs(codec.encoders))
        print("Available decoders:", self._list_codecs(codec.decoders))

    def get_files(self, obj, name, _depth=0):
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
            items += self.get_files(decoder, name, _depth+1)
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
                items += self.get_files(item, _depth+1)
            log.debug("%s => %s", obj, items)
        return items

    def extract_recursive(self, path, dest, dry=False):
        with FileReader(path, 'rb') as file:
            decoder = codec.getDecoderForFile(file)
            decoder = decoder(file, None)
            items   = self.get_files(decoder, path)
            for item in items:
                log.info("Extracting %s/%s...", dest, item['name'])
                if not dry:
                    with FileWriter(dest+'/'+item['name']) as output:
                        if 'file' in item:
                            item['file'].seek(0)
                            output.write(item['file'].read())
                        else:
                            output.write(item['obj'].toData())

    def _list_recursive(self, obj, _depth=0):
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
                self._list_recursive(item, _depth+1)

    def list_file_recursive(self, path):
        """Print list of given file's contents recursively."""
        with FileReader(path, 'rb') as file:
            decoder = codec.getDecoderForFile(file)
            decoder = decoder(file, None)
            items   = []
            for obj in decoder.objects:
                self._list_recursive(obj)

    def list_file(self, path):
        """Print list of given file's contents."""
        with FileReader(path, 'rb') as file:
            decoder = codec.getDecoderForFile(file)
            decoder = decoder(file, None)
            decoder.printList()
