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
import gpsvideo

data = []

for arg in sys.argv[1:]:
    data.append(gpsvideo.nmea.Nmea(arg))

pylab.figure()
for d in data:
    pylab.plot(d.rtimes,d.speeds)
pylab.xlabel('time (s)')
pylab.ylabel('speed (mph)')

pylab.figure()
for d in data:
    pylab.plot(d.rtimes,d.altitudes)
pylab.xlabel('time (s)')
pylab.ylabel('altitude (m)')

pylab.figure()
for d in data:
    pylab.plot(d.lons,d.lats)
pylab.xlabel('latitude (deg)')
pylab.ylabel('longitude (deg)')


pylab.show()


