#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Copyright (C) 2010,2011  Roland Arsenault

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
import gpsvideo

if len(sys.argv) < 2:
    print ('usage: mov2nmea.py [-ts] [-debug] file1.mov [file2.mov ...]')
    sys.exit(1)

args = []
timestamp = False
debug = False

for a in sys.argv[1:]:
    if a.startswith('-'):
        if a == '-ts':
            timestamp = True
        if a == '-debug':
            debug = True
    else:
        args.append(a)

for a in args:
    qt = gpsvideo.qt.QTFile(a)
    print (a)
    outfile = open(a+'.nmea','wt')
    #qt.Print()
    tracks = qt.find('moov')[0][1].find('trak')
    text_tracks = []
    for t in tracks:
        if t[1].find('mdia')[0][1].find('hdlr')[0][1].componentSubType == b'text':
            #t[1].Print('')
            sc = gpsvideo.qt.SampleCursor(t[1])
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
                        lines = tt[2][1].decode('utf_8','ignore').split()
                        for l in lines:
                            if debug:
                                nmea = l
                            else:
                                nmea = gpsvideo.nmea.FindNmea(l)
                            if nmea is not None:
                                if timestamp:
                                    outfile.write(str(nextSampleTime/float(tt[3]))+',')
                                outfile.write(nmea+'\n')
                        tt[2] = tt[1].nextSample()

        done = True
        for tt in text_tracks:
            if tt[2] is not None:
                done = False


