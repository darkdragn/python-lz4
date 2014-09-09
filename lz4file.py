#!/usr/bin/python

import __builtin__
import lz4
import struct

class Lz4File:
    MAGIC = '0x184d2204'
    
    def __init__(self, name, fileObj=None):
        self.lz4sd = lz4.Lz4sd_t()
        self.name = name
        if fileObj:
            self.fileObj = fileObj
            self.end = tell_end(fileObj)
        else:
            return open(name)
    @classmethod
    def open(cls, name = None, fileObj = None):
        if not name and not fileObj:
            sys.stderr.write('Nothing to open!')
        fileObj = __builtin__.open(name)
        magic = struct.unpack('<I', fileObj.read(4))[0]
        if not cls.MAGIC == hex(magic):
             sys.stderr.write('Invalid magic number!')
             
        des = fileObj.read(3)
        
        cls.version    = (ord(des[0]) >> 6) & 3   # 2 bits
        cls.blkIndepen = (ord(des[0]) >> 5) & 1   # 1 bit
        cls.blkChk     = (ord(des[0]) >> 4) & 1   # 1 bit
        cls.streamSize = (ord(des[0]) >> 3) & 1   # 1 bit
        cls.streamChk  = (ord(des[0]) >> 2) & 1   # 1 bit
        cls.reserved1  = (ord(des[0]) >> 1) & 1   # 1 bit
        cls.dictionary = (ord(des[0]) >> 0) & 1   # 1 bit
        
        cls.reserved2  = (ord(des[1]) >> 7) & 1   # 1 bit
        cls.blkSizeID  = (ord(des[1]) >> 4) & 7   # 3 bits
        cls.reserved3  = (ord(des[1]) >> 0) & 15  # 4 bits
        
        cls.chkBits    = (ord(des[2]) >> 0) & 255 # 8 bits
        
        return cls(name, fileObj)
    def read_block(self):
        blkSize=struct.unpack('<I', self.fileObj.read(4))[0]
        if blkSize == 0: return ''
        compData = struct.unpack('<%ds' % blkSize, 
                               self.fileObj.read(blkSize))[0]
        data = lz4.uncompress_continue(compData, self.lz4sd, 
                                        self.blkSizeID)
        return data
    def read(self, internal = 0):
        out = str()
        pos=self.fileObj.tell()
        while pos+4 < self.end:
            out += self.read_block()
            pos = self.fileObj.tell()
        return out
    def decompress(self, outName):
        pos = self.fileObj.tell()
        self.fileObj.seek(7)
        out = self.read()
        with __builtin__.open(outName, 'wb') as o:
            o.write(out)
            o.flush()
            o.close()
        self.fileObj.seek(pos)
def open(name):
    return Lz4File.open(name)
def tell_end(fileObj):
    pos = fileObj.tell()
    fileObj.seek(0, 2)
    end = fileObj.tell()
    fileObj.seek(pos)
    return end
