#!/usr/bin/env python

import subprocess

svninfo = subprocess.check_output(['svn','info'])

for line in svninfo.splitlines():
    line = line.strip()
    if len(line):
        parts = line.split()
        if parts[0] == 'Revision:':
            version = int(parts[1])
            version += 1
            open('VERSION','w').write('1.0.'+str(version)+'\n')
            break
        
