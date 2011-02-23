#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Copyright (C) 2011  Roland Arsenault

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
import pylab
import calendar
import datetime

times = []
rtimes = []
speeds = []
altitudes = []
lats = []
lons = []

for arg in sys.argv[1:]:
    times.append([])
    rtimes.append([])
    speeds.append([])
    altitudes.append([])
    lats.append([])
    lons.append([])
    for l in file(arg):
        s = l.strip()
        n = s.split(',')
        if len(n) >= 12:
            if n[1] == '$GPRMC':
                n = n[1:]
            if n[0] == '$GPRMC':
                if len(n) >= 12 and n[2] == 'A':
                    ts = n[1].split('.')[0]
                    try:
                        fs = float('.'+n[1].split('.')[1])
                        ds = n[9]
                        timestamp = calendar.timegm( datetime.datetime(int(ds[4:6])+2000,int(ds[2:4]),int(ds[0:2]),int(ts[0:2]),int(ts[2:4]),int(ts[4:6])).utctimetuple()) + fs
                        sog = float(n[7])
                        lat = float(n[3][0:2])+float(n[3][2:])/60.0
                        if n[4] == 'S':
                            lat = -lat
                        lon =  float(n[5][0:3])+float(n[5][3:])/60.0
                        if n[6] == 'W':
                            lon = -lon
                        if len(times[-1]) and timestamp < times[-1][-1]:
                            print n
                        else:
                            times[-1].append(timestamp)
                            speeds[-1].append(sog*1.15)
                            lats[-1].append(lat)
                            lons[-1].append(lon)
                    except ValueError:
                        pass

        if len(n) >= 15:
            if n[1] == '$GPGGA':
                n = n[1:]
            if n[0] == '$GPGGA':
                if len(n) >= 15:
                    try:
                        a = float(n[9])
                        while len(altitudes[-1]) < len(times[-1]):
                            altitudes[-1].append(a)
                    except ValueError:
                        pass

    if len(altitudes[-1]):
        while len(altitudes[-1]) < len(times[-1]):
            altitudes[-1].append(altitudes[-1][-1])

    for t in times[-1]:
        rtimes[-1].append(t-times[-1][0])

pylab.figure()
for i in range(len(rtimes)):
    pylab.plot(rtimes[i],speeds[i])
pylab.xlabel('time (s)')
pylab.ylabel('speed (mph)')

pylab.figure()
for i in range(len(rtimes)):
    pylab.plot(rtimes[i],altitudes[i])
pylab.xlabel('time (s)')
pylab.ylabel('altitude (m)')

pylab.figure()
for i in range(len(rtimes)):
    pylab.plot(lons[i],lats[i])
pylab.xlabel('latitude (deg)')
pylab.ylabel('longitude (deg)')


pylab.show()


