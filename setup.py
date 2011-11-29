#!/usr/bin/env python

from distutils.core import setup

setup(name='mov2nmea',
      version=open('VERSION').readline().strip(),
      description='Extracts GPS data from mov files',
      author='Roland Arsenault',
      author_email='roland@rolker.net',
      url='http://code.google.com/p/mov2nmea/',
      package_dir={'':'src'},
      packages=['gpsvideo'],
      scripts=['scripts/mov2nmea.py','scripts/plot_nmea.py'],
     )
    