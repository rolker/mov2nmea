#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Copyright (C) 2010  Roland Arsenault

#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import sys
import struct

class Atom:
    def __init__(self,infile,pos=None,end=None):
        self.infile = infile
        if pos is None:
            self.startPosition = infile.tell()
        else:
            self.startPosition = pos
            infile.seek(pos)

        if end is None:
            self.infile.seek(0,2)
            self.endOfStorage = self.infile.tell()
            self.infile.seek(self.startPosition)
        else:
            self.endOfStorage = end

        if self.endOfStorage - self.startPosition >= 8:
            header = self.unpack('!I4s')
        else:
            header = None

        if header is None:
            self.size = 0
            self.type = None
            return

        self.size = header[0]
        self.type = header[1].decode('utf-8')

        self.dataOffset = 8

        if self.size == 0: # to end of file
            self.size = self.endOfStorage- self.startPosition

        if self.size == 1:
            s = self.unpack('!Q')
            if s is None:
                print ('Error reading extended size')
                self.size = None
                return
            self.size = s[0]
            self.dataOffset = 16

    def Print(self,indent=''):
        print (indent + self.type + ' ' + str(self.size))

    def valid(self):
        return self.type is not None and self.size >= self.dataOffset and self.endOfStorage >= self.startPosition + self.size

    def unpack(self,fmt):
        fsize = struct.calcsize(fmt)
        data = self.infile.read(fsize)
        if len(data) == fsize:
            return struct.unpack(fmt,data)

    def unpackData(self,fmt,offset=0):
        self.infile.seek(self.startPosition+self.dataOffset+offset)
        return self.unpack(fmt)

    def dataSize(self):
        return self.size - self.dataOffset

    def nextAtom(self):
        return  Atom(self.infile,self.startPosition+self.size,self.endOfStorage)

    def childAtom(self,offset = 0):
        return Atom(self.infile,self.startPosition+self.dataOffset+offset,self.startPosition+self.size)


class ContainerAtom:
    def __init__(self,atom=None,atomMap=None,infile=None,offset=0,count=None):
        self.children = []
        if atom is None:
            ca = Atom(infile)
        else:
            ca = atom.childAtom(offset)
        while ca.valid():
            if atomMap is not None and ca.type in  atomMap: #   .has_key(ca.type):
                self.children.append((ca,atomMap[ca.type](ca)))
            else:
                self.children.append([ca,None])
            if count is not None and len(self.children) >= count:
                break
            ca = ca.nextAtom()

    def find(self,atype):
        ret = []
        for ca in self.children:
            if ca[0].type == atype:
                ret.append(ca)
        return ret

    def Print(self,indent=''):
        for ca in self.children:
            ca[0].Print(indent+'  ')
            if ca[1] is not None:
                ca[1].Print(indent+'    ')





class FileTypeAtom:
    def __init__(self,atom):
        self.majorBrand = atom.unpackData('!4s')[0]
        self.minorVersion = atom.unpackData('!3B',4)
        fmt = '!'+('4s'*(int(atom.dataSize()/4)-2))
        self.compatibleBrands = atom.unpackData(fmt,8)

    def Print(self,indent):
        print (indent + str(self.majorBrand))
        print (indent + str(self.minorVersion))
        print (indent + str(self.compatibleBrands))



class LeafAtom:
    def __init__(self,atom):
        self.version = atom.unpackData('!B',0)[0]
        self.flags = atom.unpackData('!3B',1)

    def Print(self,indent):
        print (indent + 'version: ' + str(self.version))
        print (indent + 'flags: '+str(self.flags))

class HeaderAtom(LeafAtom):
    def __init__(self,atom):
        LeafAtom.__init__(self,atom)
        self.creationTime = atom.unpackData('!I',4)[0]
        self.modificationTime = atom.unpackData('!I',8)[0]

    def Print(self,indent):
        LeafAtom.Print(self,indent)
        print (indent + 'creation: ' + str(self.creationTime))
        print (indent + 'modification: ' + str(self.modificationTime))

class MovieHeaderAtom(HeaderAtom):
    def __init__(self,atom):
        HeaderAtom.__init__(self,atom)

        self.timeScale = atom.unpackData('!I',12)[0]
        self.duration = atom.unpackData('!I',16)[0]

    def Print(self,indent):
        HeaderAtom.Print(self,indent)
        print (indent + 'time scale: '+str(self.timeScale))
        print (indent + 'duration: '+str(self.duration)+' ('+str(self.duration/float(self.timeScale))+'s)')


class UserDataAtom (ContainerAtom):
    def __init__(self,atom):
        ContainerAtom.__init__(self,atom)



class TrackHeaderAtom(HeaderAtom):
    def __init__(self,atom):
        HeaderAtom.__init__(self,atom)

        self.trackID = atom.unpackData('!I',12)[0]
        self.width = atom.unpackData('!I',74)[0]
        self.height = atom.unpackData('!I',78)[0]

    def Print(self,indent):
        HeaderAtom.Print(self,indent)
        print (indent + 'ID: '+str(self.trackID))
        print (indent + 'W x H: '+str(self.width)+' x '+str(self.height))


class TableAtom(LeafAtom):
    def __init__(self,atom,fmt,offset=4):
        LeafAtom.__init__(self,atom)
        self.data = []
        if atom.size > atom.dataOffset+offset:
            numEntries = atom.unpackData('!I',offset)[0]
            fmtSize = struct.calcsize(fmt)
            for i in range(numEntries):
                d = atom.unpackData(fmt,offset+4+i*fmtSize)
                if len(d) > 1:
                    self.data.append(d)
                else:
                    self.data.append(d[0])

    def Print(self,indent):
        LeafAtom.Print(self,indent)
        print (indent + str(len(self.data)) + ' data items')
        for i in range(len(self.data)):
            if i >= 10:
                break
            print (indent + '  ' + str(self.data[i]))

class EditListAtom(TableAtom):
    def __init__(self,atom):
        TableAtom.__init__(self,atom,'!3I')


class EditAtom(ContainerAtom):
    atomMap = {'elst':EditListAtom}

    def __init__(self,atom):
        ContainerAtom.__init__(self,atom,EditAtom.atomMap)


class MediaHeaderAtom(HeaderAtom):
    def __init__(self,atom):
        HeaderAtom.__init__(self,atom)

        self.timeScale = atom.unpackData('!I',12)[0]
        self.duration = atom.unpackData('!I',16)[0]

    def Print(self,indent):
        HeaderAtom.Print(self,indent)
        print (indent + 'time scale: '+str(self.timeScale))
        print (indent + 'duration: '+str(self.duration)+' ('+str(self.duration/float(self.timeScale))+'s)')


class HandlerReferenceAtom(LeafAtom):
    def __init__(self,atom):
        LeafAtom.__init__(self,atom)

        self.componentType = atom.unpackData('!4s',4)[0]
        self.componentSubType = atom.unpackData('!4s',8)[0]
        ssize = atom.unpackData('!B',24)[0]
        if ssize > 0:
            self.componentName = atom.unpackData('!'+str(ssize)+'s',25)[0]
        else:
            self.componentName = None

    def Print(self,indent):
        LeafAtom.Print(self,indent)
        print (indent + 'component type: ' + str(self.componentType))
        print (indent + 'component subtype: ' + str(self.componentSubType))
        print (indent + 'component name: ' + str(self.componentName))

class BaseMediaInformationAtom(ContainerAtom):
    atomMap = {}

    def __init__(self,atom):
        ContainerAtom.__init__(self,atom,BaseMediaInformationAtom.atomMap)

class CountedContainerAtom(LeafAtom,ContainerAtom):
    def __init__(self,atom,atomMap):
        LeafAtom.__init__(self,atom)
        self.numEntries = atom.unpackData('!I',4)[0]
        ContainerAtom.__init__(self,atom,atomMap,offset=8,count=self.numEntries)

    def Print(self,indent):
        LeafAtom.Print(self,indent)
        print (indent + str(self.numEntries) + ' entries')
        ContainerAtom.Print(self,indent)


class DataReferenceAtom(CountedContainerAtom):
    atomMap = {}

    def __init__(self,atom):
        CountedContainerAtom.__init__(self,atom,DataReferenceAtom.atomMap)


class DataInformationAtom(ContainerAtom):
    atomMap = {'dref':DataReferenceAtom}

    def __init__(self,atom):
        ContainerAtom.__init__(self,atom,DataInformationAtom.atomMap)

class SampleDescription:
    def __init__(self,atom):
        self.dataReferenceIndex = atom.unpackData('!H',6)[0]

    def Print(self,indent):
        print (indent + 'data ref index: ' + str(self.dataReferenceIndex))

class TextSampleDescription(SampleDescription):
    def __init__(self,atom):
        SampleDescription.__init__(self,atom)
        self.displayFlags = atom.unpackData('!I',8)[0]
        self.textJustification = atom.unpackData('!I',12)[0]
        self.bgColor = atom.unpackData('!3H',16)
        self.textBox = atom.unpackData('!4H',22)
        self.fontNumber = atom.unpackData('!H',38)[0]
        self.fontFace = atom.unpackData('!H',40)[0]
        self.fgColor = atom.unpackData('!3H',45)
        tsize = atom.size - (atom.dataOffset + 51)
        if tsize > 0:
            self.name = atom.unpackData('!'+str(tsize)+'s',51)[0]
        else:
            self.name = None

    def Print(self,indent):
        SampleDescription.Print(self,indent)
        print (indent + ','.join((str(self.displayFlags),str(self.textJustification),str(self.bgColor),str(self.textBox),str(self.fontNumber),str(self.fontFace),str(self.fgColor))))
        print (indent + str(self.name))

class SampleDescriptionAtom(CountedContainerAtom):
    atomMap = {'text':TextSampleDescription}

    def __init__(self,atom):
        CountedContainerAtom.__init__(self,atom,SampleDescriptionAtom.atomMap)

class TimeToSampleAtom(TableAtom):
    def __init__(self,atom):
        TableAtom.__init__(self,atom,'!2I')

class SyncSampleAtom(TableAtom):
    def __init__(self,atom):
        TableAtom.__init__(self,atom,'!I')

class SampleToChunkAtom(TableAtom):
    def __init__(self,atom):
        TableAtom.__init__(self,atom,'!3I')

class SampleSizeAtom(TableAtom):
    def __init__(self,atom):
        self.sampleSize = atom.unpackData('!I',4)[0]
        TableAtom.__init__(self,atom,'!I',8)

    def Print(self,indent):
        print (indent + 'sample size:'+str(self.sampleSize))
        TableAtom.Print(self,indent)

class ChunkOffsetAtom(TableAtom):
    def __init__(self,atom):
        TableAtom.__init__(self,atom,'!I')

class ChunkOffset64Atom(TableAtom):
    def __init__(self,atom):
        TableAtom.__init__(self,atom,'!Q')


class SampleTableAtom(ContainerAtom):
    atomMap = {'stsd':SampleDescriptionAtom, 'stts':TimeToSampleAtom, 'stss':SyncSampleAtom, 'stsc':SampleToChunkAtom, 'stsz':SampleSizeAtom, 'stco':ChunkOffsetAtom, 'co64':ChunkOffset64Atom}

    def __init__(self,atom):
        ContainerAtom.__init__(self,atom,SampleTableAtom.atomMap)

class MediaInformationAtom(ContainerAtom):
    atomMap = {'hdlr':HandlerReferenceAtom,'gmhd':BaseMediaInformationAtom,'dinf':DataInformationAtom,'stbl':SampleTableAtom}

    def __init__(self,atom):
        ContainerAtom.__init__(self,atom,MediaInformationAtom.atomMap)


class MediaAtom(ContainerAtom):
    atomMap = {'mdhd':MediaHeaderAtom, 'hdlr':HandlerReferenceAtom, 'minf':MediaInformationAtom}
    def __init__(self,atom):
        ContainerAtom.__init__(self,atom,MediaAtom.atomMap)


class TrackAtom(ContainerAtom):
    atomMap = {'tkhd':TrackHeaderAtom, 'edts':EditAtom, 'mdia':MediaAtom}

    def __init__(self,atom):
        ContainerAtom.__init__(self,atom,TrackAtom.atomMap)

class MovieAtom (ContainerAtom):
    atomMap = {'mvhd':MovieHeaderAtom, 'udta':UserDataAtom, 'trak':TrackAtom}
    def __init__(self,atom):
        ContainerAtom.__init__(self,atom,MovieAtom.atomMap)


class QTFile(ContainerAtom):
    atomMap = {'ftyp':FileTypeAtom, 'moov':MovieAtom}

    def __init__(self,fname):
        infile = open(fname,'rb')
        ContainerAtom.__init__(self,None,QTFile.atomMap,infile)


class SampleCursor:
    def __init__(self,track):
        m = track.find('mdia')[0][1]
        self.infile = track.children[0][0].infile

        minf = m.find('minf')[0][1]
        st = minf.find('stbl')[0][1]

        self.sampleNumber = 0

        self.sampleDurations = st.find('stts')[0][1]
        self.sampleTime = 0
        self.sampleDurationIndex = 0
        self.sampleInDuration = 0

        self.sampleSizes = st.find('stsz')[0][1]

        self.sampleToChunk = st.find('stsc')[0][1]
        self.sc_index = 0

        self.chunkOffsets = st.find('stco')[0][1]
        self.chunkNumber = 0
        self.sampleInChunk = 0

    def nextSample(self):
        ss = self.sampleSizes.sampleSize
        if ss == 0:
            if len(self.sampleSizes.data) <= self.sampleNumber:
                return None
            ss = self.sampleSizes.data[self.sampleNumber]

        self.sampleInChunk += 1
        if(self.sampleToChunk.data[self.sc_index][1] >= self.sampleInChunk):
            self.sampleInChunk = 0
            self.chunkNumber += 1

        while len(self.sampleToChunk.data) > self.sc_index+1 and self.sampleToChunk.data[self.sc_index+1][0] < self.chunkNumber:
            self.sc_index += 1

        if len(self.chunkOffsets.data) <= self.chunkNumber:
            return None

        so = self.chunkOffsets.data[self.chunkNumber]

        self.infile.seek(so)
        data = self.infile.read(ss)
        ret = (self.sampleTime,data)
        self.sampleTime += self.sampleDurations.data[self.sampleDurationIndex][1]
        self.sampleInDuration += 1
        if len(self.sampleDurations.data) >= self.sampleDurationIndex and self.sampleInDuration >= self.sampleDurations.data[self.sampleDurationIndex][0]:
            self.sampleInDuration = 0
            self.sampleDurationIndex += 1

        self.sampleNumber += 1

        return ret

def LooksValid(nmea):
    return len(nmea) >= 3 and nmea[0] == '$' and nmea[-3] == '*'

if len(sys.argv) < 2:
    print ('usage: mov2nmea.py file1.mov [file2.mov ...]')
    sys.exit(1)

for a in sys.argv[1:]:
    qt = QTFile(a)
    print (a)
    outfile = open(a+'.nmea','w')
    #qt.Print()
    tracks = qt.find('moov')[0][1].find('trak')
    text_tracks = []
    for t in tracks:
        if t[1].find('mdia')[0][1].find('hdlr')[0][1].componentSubType == b'text':
            #t[1].Print('')
            sc = SampleCursor(t[1])
            s = sc.nextSample()
            tid = t[1].find('tkhd')[0][1].trackID
            ts = t[1].find('mdia')[0][1].find('mdhd')[0][1].timeScale
            text_tracks.append([tid,sc,s,ts])

    done = False
    while not done:
        nextSampleTime = None

        for tt in text_tracks:
            if tt[2] is not None:
                if nextSampleTime is None:
                    nextSampleTime = tt[2][0]
                else:
                    if tt[2][0] < nextSampleTime:
                        nextSampleTime = tt[2][0]

        if nextSampleTime is not None:
            for tt in text_tracks:
                if tt[2] is not None:
                    if tt[2][0] == nextSampleTime:
                        lines = tt[2][1].decode('utf-8','ignore').split()
                        for l in lines:
                            if LooksValid(l):
                                #print ','.join((str(nextSampleTime/float(tt[3])),l))
                                outfile.write(','.join((str(nextSampleTime/float(tt[3])),l))+'\n')
                            #print ','.join((str(nextSampleTime),str(tt[0]),l))
                        tt[2] = tt[1].nextSample()

        done = True
        for tt in text_tracks:
            if tt[2] is not None:
                done = False


