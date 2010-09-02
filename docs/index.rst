.. CSVSee documentation master file, created by
   sphinx-quickstart on Fri Aug 20 15:59:31 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

CSVSee
======

You are reading the documentation for CSVSee_, a set of tools for manipulating
and visualizing data in comma-separated (CSV) files.

.. _CSVSee: http://www.automation-excellence.com/software/csvsee


Motivation
----------
This toolkit was originally developed to help with analyzing test results
coming from Grinder_ and Performance Monitor. It was partly inspired by
`Grinder Analyzer`_, which serves a similar purpose in a more specific domain.

.. _Grinder: http://grinder.sourceforge.net/
.. _Grinder Analyzer: http://track.sourceforge.net/

Features
--------
* Generate graphs of just about any numerical data, particularly those having timestamps
* Match one or more CSV column names with regular expressions
* Automatic color-coding when graphing multiple columns
* Display graphs in an interactive viewer with zooming/panning capability
* Export graphs to a ``.png``, ``.svg`` or ``.pdf`` file
* Customizable line styles, title / axis labels, and timestamp formats
* Plot the top ``N`` data sets, by average or peak value within each column


License
-------
This software is open source, under the terms of the `simplified BSD license`_.

.. _simplified BSD license: http://www.opensource.org/licenses/bsd-license.php


Installation
------------
To install CSVSee, obtain a copy of the branch from Launchpad_ using Bazaar_::

    bzr branch lp:csvsee

At present, there are no official release packages, and no installed components.

All of the scripts require Python_. The ``csvgraph.py`` script also depends on
matplotlib_ and NumPy_.

.. _Launchpad: https://code.launchpad.net/csvsee
.. _Bazaar: http://bazaar.canonical.com/
.. _Python: http://python.org/download/
.. _matplotlib: http://sourceforge.net/projects/matplotlib/files/matplotlib/matplotlib-0.99.1/
.. _NumPy: http://sourceforge.net/projects/numpy/files/


Scripts and modules
-------------------

.. toctree::
    :maxdepth: 2

    csvsee
    csvgraph
    csvgrep

