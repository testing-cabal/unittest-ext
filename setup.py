#!/usr/bin/env python

from distutils.core import setup

import discover

description = 'Test discovery for unittest. Backported from Python 2.7 for Python 2.4+'
setup(name='discover',
      version=discover.__version__,
      description=description,
      author='Michael Foord',
      author_email='michael@voidspace.org.uk',
      url='http://pypi.python.org/pypi/discover/',
      py_modules=['discover'],
     )
