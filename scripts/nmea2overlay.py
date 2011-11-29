#!/usr/bin/env python

import sys
import nmea
import os

template = '''<svg xmlns="http://www.w3.org/2000/svg" height="1080" width="1920">
<text x="50" y="100" font-size="100" fill="white" stroke="black" stroke-width="2">{:.0f} mph</text>
</svg>
'''

n = nmea.Nmea(sys.argv[1])

outpath = sys.argv[2]

for i in range(len(n.speeds)):
    outname = os.path.join(outpath,'file{0:05}.svg'.format(int(n.timestamps[i])))
    print outname,n.speeds[i],n.timestamps[i]
    out = open(outname,'w')
    out.write(template.format(n.speeds[i]))
    out.close()
    