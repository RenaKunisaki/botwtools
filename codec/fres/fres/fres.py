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
from structreader import readStringWithLength, readString
from .header   import Header
from .idxgrp   import IndexGroup
from .embedded import EmbeddedFile
from .fmdl     import FMDL
from .rlt      import RLT
from codec.base.strtab import StringTable

class FRES:
    """Represents an FRES archive."""

    object_types = (
        # types of objects embedded in FRES.
        # (name, class)
        ('fmdl', FMDL),
        #('fska', FSKA),
        #('fmaa', FMAA),
        #('fvis', FVIS),
        #('fscn', FSCN),
        #('fshu', FSHU),
        ('embed',  EmbeddedFile),
    )

    def __init__(self):
        self.objects = []


    def readFromFile(self, file):
        """Read the archive from given file."""
        self.file   = file
        self.header = Header().readFromFile(file)
        self.header.fres = self # for dumpOffsets
        self.rlt    = None # for dumpOffsets
        log.debug("FRES version: 0x%08X", self.header.version)

        # name is NOT length-prefixed but name2 is.
        # usually they both point to the same string, just with
        # name skipping the prefix.
        self.name = readString(self.file, self.header.name_offset)
        log.debug("FRES name='%s'", self.name)
        self.name2 = self.readStr(self.header.name2)
        log.debug("FRES name2='%s'", self.name2)

        if self.header.type == 'switch': self.readRLT()
        else: self.rlt = None

        self.header.dumpToDebugLog()
        self.header.dumpOffsets()

        self.strtab = self.readStringTable(
            self.header.str_tab_offset - 0x14) # WTF?

        for typ in self.object_types:
            self.readObjects(*typ)

        return self


    def getNumObjects(self, typ):
        return getattr(self.header, typ+'_cnt')

    def getObjects(self, typ):
        return getattr(self, typ+'s')

    def getObjectGroups(self, typ):
        return getattr(self, typ+'_groups')


    def readObjects(self, typ, cls):
        offs = getattr(self.header, '%s_offset' % typ)
        cnt  = getattr(self.header, '%s_cnt' % typ)
        dofs = getattr(self.header, '%s_dict_offset' % typ)
        objs = []
        size = cls._reader.size
        groups = []
        log.debug("Reading %d %s from 0x%X (dict 0x%X)",
            cnt, typ, offs, dofs)
        for i in range(cnt):
            group = IndexGroup().readFromFile(self.file, dofs+(i*8))
            groups.append(group)
            log.debug("FRES %s %d: %s", type(cls).__name__, i, group.dump())
            obj = cls().readFromFRES(self, offs+(i*size))
            objs.append(obj)
            if obj.name is None:
                obj.name = group.root.left.name
        setattr(self, typ+'s', objs)
        setattr(self, typ+'_groups', groups)


    def readRLT(self):
        self.rlt = RLT().readFromFile(self.file, self.header.rlt_offset)
        log.debug("RLT @%06X starts at %06X",
            self.header.rlt_offset, self.rlt.data_start)
        assert self.rlt.data_start < self.file.size, \
            "RlT start 0x%X is beyond EOF 0x%X" % (
                self.rlt.data_start, self.file.size)
        self.rlt.fres = self
        self.rlt.dumpToDebugLog()
        self.rlt.dumpOffsets()


    def readStringTable(self, offset):
        return StringTable().readFromFile(self.file, offset)


    def read(self, size:(int,str)=-1, pos:int=None, count:int=1,
    use_rlt:bool=False):
        """Read data from the file.

        size:    Number of bytes, or struct format string.
        pos:     Position to seek to before reading.
        count:   Number of items to read. If not 1, returns a list.
        use_rlt: Whether to add the RLT offset (if any) to the
            file read position.

        Returns the data.
        """
        if use_rlt and (self.rlt is not None):
            # apply RLT offset
            if pos is None: pos = self.file.tell()
            log.debug("read: 0x%X + RLT 0x%X = 0x%X (size=0x%X)",
                pos,  self.rlt.data_start,
                pos + self.rlt.data_start,
                self.file.size)
            pos += self.rlt.data_start

        # validate range
        if type(size) is str: sz = struct.calcsize(size)
        else: sz = size
        if sz > 0 and pos + (sz * count) >= self.file.size:
            log.error("Reading beyond EOF "
                "(pos 0x%X size 0x%X => 0x%X, EOF is 0x%X)",
                pos, (sz*count), pos+(sz*count), self.file.size)

        # read data
        if count < 0:
            raise ValueError("Count cannot be negative")
        elif count == 0: return []
        elif count == 1:
            return self.file.read(size, pos)
        else:
            res = []
            if pos is not None: self.file.seek(pos)
            for i in range(count):
                res.append(self.file.read(size))
            return res


    def readStr(self, offset):
        """Read string (prefixed with length) from given offset."""
        return readStringWithLength(self.file, '<H', offset)


    def readHex(self, cnt, offset):
        """Read hex string for debugging."""
        data = self.read(cnt, offset)
        hx   = map(lambda b: '%02X' % b, data)
        return ' '.join(hx)
