#!/usr/bin/python2.7
import lz4, struct

class testIt:
    def __init__(self):
        lz4sd=lz4.Lz4sd_t()
        f=open('testOrig.lz4')
        f.seek(7)
        self.blkSize=struct.unpack('<I', f.read(4))[0]
        self.compData=struct.unpack('<%ds' % self.blkSize, f.read(self.blkSize))[0]
        self.data=lz4.uncompress_continue(self.compData, lz4sd, 7)
        
        self.lz4sd=lz4sd
        self.f=f
    def writeTest(self, testName):
        with open(testName, 'wb') as o:
            o.write(self.data)
            o.flush()
            o.close()
