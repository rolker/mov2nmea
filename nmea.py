#!/usr/bin/env python

import calendar
import datetime

class Nmea:
    def __init__(self,fname):
        self.times = []
        self.rtimes = []
        self.speeds = []
        self.altitudes = []
        self.lats = []
        self.lons = []
        self.timestamps = []

        for l in file(fname):
            s = l.strip()
            n = s.split(',')
            if len(n) >= 12:
                if n[1] == '$GPRMC':
                    self.timestamps.append(float(n[0]))
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
                            if len(self.times) and timestamp < self.times[-1]:
                                print n
                            else:
                                self.times.append(timestamp)
                                self.speeds.append(sog*1.15)
                                self.lats.append(lat)
                                self.lons.append(lon)
                        except ValueError:
                            pass

            if len(n) >= 15:
                if n[1] == '$GPGGA':
                    n = n[1:]
                if n[0] == '$GPGGA':
                    if len(n) >= 15:
                        try:
                            a = float(n[9])
                            while len(self.altitudes) < len(self.times):
                                self.altitudes.append(a)
                        except ValueError:
                            pass

        if len(self.altitudes):
            while len(self.altitudes) < len(self.times):
                self.altitudes.append(self.altitudes[-1])

        for t in self.times:
            self.rtimes.append(t-self.times[0])
