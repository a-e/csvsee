#! /usr/bin/env python
# setup.py

"""Installer for CSVSee.
"""

from distutils.core import setup

setup(name='CSVSee',
      version='0.2',
      description='Visualization and manipulation of CSV files.',
      author='Eric Pierce',
      author_email='wapcaplet88@gmail.com',
      url='http://www.automation-excellence.com/software/csvsee',
      license='Simplified BSD License',
      packages=['csvsee'],
      scripts=['csvs'],
     )


