Development
===========

If you'd like to hack on CSVSee, you'll probably want to install the development
dependencies first::

    $ pip install -r dev-req.txt


Testing
-------
.. versionadded:: 0.2

CSVSee's core modules include several doctests_, along with a suite of unit
tests in the ``tests`` directory that can be run with py.test_::

    $ py.test

To generate a coverage_ report, you can just get a plain-text report::

    $ py.test --cov csvsee --cov-report=term-missing

Or a nice HTML report::

    $ py.test --cov csvsee --cov-report=html

.. _doctests: http://docs.python.org/library/doctest.html
.. _py.test: http://pytest.org/
.. _coverage: http://nedbatchelder.com/code/coverage/

