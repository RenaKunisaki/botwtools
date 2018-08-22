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
from lxml import etree as ET

class Element:
    def __init__(self, _element_name, *children, **attrs):
        self.name      = _element_name
        self.attrs     = attrs
        self._text     = None
        self._children = list(children)
        self.parent    = None


    def Child(self, _element_name, *children, **attrs):
        child = Element(_element_name, *children, **attrs)
        self.append(child)
        return child


    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, t):
        self._text = t


    @property
    def children(self):
        return self._children


    def append(self, child):
        if type(child) is str:
            if self._text is None: self._text = child
            else: self._text += child
        elif isinstance(child, Element):
            if child.parent is not None:
                log.warn("Element '%s' already has a parent '%s'",
                    child.name, child.parent.name)
            child.parent = self
            self._children.append(child)
        else:
            raise TypeError(
                "Element.append: Expected str or Element, got %s" %
                type(child).__name__)


    def get(self, name, *default):
        return self.attrs.get(name, *default)


    def set(self, name, *val):
        if type(name) is dict:
            for k, v in name.items(): self.attrs[k] = v
        else:
            self.attrs[name] = val[0]


    def _toXML(self, document):
        el = ET.Element(self.name)
        for k, v in self.attrs.items():
            if ':' in k:
                ns, k = k.split(':', maxsplit=1)
                try: uri = document.namespaces[ns]
                except KeyError:
                    raise KeyError("Namespace '%s' not defined" % ns)
                k = '{%s}%s' % (uri, k)
            el.set(k, str(v))

        if self._text is not None:
            el.text = self._text

        for child in self._children:
            if isinstance(child, Element):
                el.append(child._toXML(document))
            elif isinstance(child, ET.Element):
                el.append(child)
            else:
                # shouldn't happen because append() checks type
                assert False, "Child of type '%s' in XML element" % \
                    type(child).__name__

        return el


    def __str__(self):
        return "<XML Element '%s' at 0x%X>" % (self.name, id(self))
