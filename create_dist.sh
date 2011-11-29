#!/bin/sh

./update_version.py
cat VERSION
python setup.py sdist bdist_wininst
