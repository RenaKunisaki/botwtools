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

import logging; log = logging.getLogger()
from lxml import etree as ET
from .element import Element

class Document:
    def __init__(self, _element_name, *children, **rootAttrs):
        self.root = Element(_element_name, *children, **rootAttrs)
        self.namespaces = {}


    def addNamespace(self, name, uri):
        if name in self.namespaces:
            raise KeyError("Namespace '%s' already registered" % name)
        self.namespaces[name] = uri


    def toXML(self):
        return ET.ElementTree(self.root._toXML(self))


    def writeToFile(self, file, encoding='utf-8',
    xml_declaration=True, **kwargs):
        return self.toXML().write(file,
            encoding=encoding,
            xml_declaration=xml_declaration,
            **kwargs)


    def __str__(self):
        return "<XML Document (root=%s) at 0x%X>" % (
            self.root.name, id(self))
