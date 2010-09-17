:mod:`csvsee`
=============

The `csvsee` module provides most of the functionality of CSVSee.
It consists of the following submodules:

.. toctree::
    :maxdepth: 2

    dates
    utils
    graph
    grinder


Testing
-------
CSVSee's core modules include several doctests_, along with a suite of unit
tests in the ``tests`` directory that can be run with nose_. If you have the
coverage_ module installed, nose will generate a report of statement coverage
in the ``coverage`` directory.

To install nose_ and coverage_::

    pip install nose
    pip install coverage

Then run this from the CSVSee source directory::

    nosetests

This will also generate a sample graph, so you can visually confirm that the
graphing feature is working as expected.

.. _doctests: http://docs.python.org/library/doctest.html
.. _nose: http://code.google.com/p/python-nose/
.. _coverage: http://nedbatchelder.com/code/coverage/
