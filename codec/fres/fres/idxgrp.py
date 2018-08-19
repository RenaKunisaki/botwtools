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
import struct


class Node:
    def __init__(self, idx, name, dataOffs, search, left, right):
        self.index    = idx
        self.name     = name
        self.dataOffs = dataOffs
        self.search   = search
        self.left     = left
        self.right    = right


class IndexGroup:
    def __init__(self):
        self.root = None


    def readFromFile(self, file, offset=None):
        if offset is not None: file.seek(offset)
        length, count = file.read('II')
        log.debug("dict(%06X) len=0x%X cnt=0x%X", offset, length, count)
        nodes = []
        for i in range(count+1): # +1 for root node
            try:
                srch, lidx, ridx, noff, doff = file.read('iHHII')
            except struct.error:
                break # XXX this shouldn't happen
            #log.debug("node %d: %08X %04X %04X %08X %08X",
            #    i, srch, lidx, ridx, noff, doff)

            if noff:
                pos = file.tell()
                try:
                    name = file.readString(noff, '<H')
                except UnicodeDecodeError:
                    name = None # XXX this shouldn't happen
                file.seek(pos)
            else:
                name = None

            nodes.append((name, doff, srch, lidx, ridx))

        def mkNode(idx, _depth=0):
            #log.debug("mkNode(%d)", idx)
            if _depth > 8: return None
            if idx == 0 and _depth > 0: return None
            try:
                name, doff, srch, lidx, ridx = nodes[idx]
            except IndexError:
                return None # XXX this shouldn't happen
            left, right = None, None
            if lidx > idx: left  = mkNode(lidx, _depth+1)
            if ridx > idx: right = mkNode(ridx, _depth+1)
            # XXX what does it mean when >0 but <idx?
            return Node(idx, name, doff, srch, left, right)

        self.root = mkNode(0)
        return self


    def dump(self, node=None, prefix='', _depth=0, ind='', isLast=False):
        """Dump to nice string for debugging."""
        if _depth == 0 and node is None:
            node = self.root

        if node is None:
            return ind+prefix+"<none>\n"

        r = '%s%s%s%d] "%s" (offs=0x%X srch=%d)\n' % (ind,
            prefix, '[root:' if _depth == 0 else '',
            node.index, node.name, node.dataOffs, node.search)

        if _depth > 0:
            ind += '  ' if isLast else '│ '
        if node.left:
            if node.right:
                p = '├'
            else:
                p = '└'
            r += self.dump(node.left,  p+'─[L:', _depth+1, ind, (not node.right))

        if node.right:
            r += self.dump(node.right, '└─[R:', _depth+1, ind, True)

        return r
