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

    def __init__(self, endian='little', readOnly=False):
        self.endian   = endian
        self.readOnly = readOnly


    def makeFileReader(self, file, mode='rb') -> FileReader:
        """Make a FileReader for the given file,
        with default settings for this app.
        """
        log.debug("makeFileReader(%s: %s)", file, getattr(file, 'name', None))
        if isinstance(file, FileReader): return file
        return FileReader(file, mode,
            endian=self.endian,
            defaultStringLengthFmt='H')


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

        # name might be int if input is a temp file,
        # so ignore it in that case.
        oname = getattr(obj, 'name', name)
        if type(oname) is str: name = oname

        if (hasattr(obj, 'defaultFileExt')
        and not name.endswith(obj.defaultFileExt)):
            name += '.' + obj.defaultFileExt

        if hasattr(obj, 'toData'):
            log.debug("recursing into %s, name=%s", obj, name)
            file = tempfile.TemporaryFile()
            data = obj.toData()
            if type(data) is str: data = bytes(data, 'utf-8')
            file.write(data)
            file.seek(0, 0)
            file = self.makeFileReader(file)
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
            #log.debug("%s => %s", obj, items)
        else:
            if not getattr(obj, 'isListable', False):
                log.debug("Can't list object: %s", obj)
                return items

            log.debug("no data in %s", obj)
            for item in getattr(obj, 'objects', []):
                items += self.get_files(item, name, _depth+1)
            #log.debug("%s => %s", obj, items)
        return items


    def get_file_name(self, obj, input):
        name = getattr(obj, 'name', input)
        if hasattr(obj, 'defaultFileExt'):
            name += '.' + obj.defaultFileExt
        return name


    def write_file(self, name, obj, dest):
        if hasattr(obj, 'toData'):
            data = obj.toData()
            path, name = os.path.split(name)
            name = self.get_file_name(obj, name)
            log.info("Extracting %s to %s...", name, dest+'/'+name)
            if not self.readOnly:
                with FileWriter(dest+'/'+name) as output:
                    output.write(data)
        else:
            for obj in obj.objects:
                self.write_file(name, obj, dest)



    def extract_file(self, path, dest):
        with self.makeFileReader(path) as file:
            decoder = codec.getDecoderForFile(file)
            decoder = decoder(file, None)
            self.write_file(path, decoder, dest)


    def extract_recursive(self, path, dest):
        with self.makeFileReader(path) as file:
            decoder = codec.getDecoderForFile(file)
            decoder = decoder(file, None)
            log.debug("get_files(%s, %s)", decoder, path)
            items   = self.get_files(decoder, path)
            for item in items:
                log.info("Extracting %s/%s...", dest, item['name'])
                if not self.readOnly:
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
            file = self.makeFileReader(file)
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


    def show_xml(self, path):
        """Read an XML file and display it in a more convenient format."""
        import xml.dom.minidom
        with open(path, 'rt') as file:
            data = file.read()
            doc  = xml.dom.minidom.parseString(data)
        def _printNode(node, parent='', _depth=0,_idx=0):
            pref = '    ' * (_depth - 2)
            #print('%s%s: %s' % (pref, node.localName,
            #    getattr(node, 'data', '').strip()))
            if node.nodeType == node.TEXT_NODE:
                data = node.data.strip()
                if data != '':
                    print('%s%-20s "%s"' % (pref, parent+':', data))
            else:
                name = ''
                if node.localName is not None:
                    name = node.localName
                if _idx == 1:
                    print('%s%s:' % (pref, parent))
                for i, child in enumerate(node.childNodes):
                    _printNode(child, parent=name,
                        _depth=_depth+1, _idx=i)
        _printNode(doc)
