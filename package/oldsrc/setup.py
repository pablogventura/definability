#!/usr/bin/env python

from distutils.core import setup

from definability import config

print "*" * 80
print ""
print "This package needs Minion and LADR."
print "Minion path: %s" % config.minion_path
print "LADR path: %s" % config.ladr_path
print "If you need to change the path, edit config.py and reinstall."
print ""
print "*" * 80

setup(name='definability',
      version='0.1',
      description='',
      author='Pablo Ventura',
      author_email='pablogventura@gmail.com',
      url='',
      packages=['definability'],
      )
