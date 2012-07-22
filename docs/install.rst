Installation
============

You'll need Python_ before doing anything else. Most Linux distributions already
have this installed, but you can use this to check::

    $ which python
    /usr/bin/python

Install pip_ too::

    $ sudo apt-get install python-pip

To use the graphing features of CSVSee, you'll need NumPy_ and matplotlib_.
These require some development headers in order to install properly; on Ubuntu,
this should work::

    $ sudo apt-get install python-dev libpng-dev

Then::

    $ pip install -r req.txt

If that doesn't work, you may need to install numpy and matplotlib separately::

    $ pip install numpy
    $ pip install matplotlib

If you want to install an official release, first download one from the
`downloads page`_, and extract it somewhere.

Then, open that directory in a terminal and run::

    $ sudo python setup.py install

Or use pip_::

    $ sudo pip install .

One advantage of using ``pip`` is that you can uninstall later like so::

    $ sudo pip uninstall CSVSee

If you'd rather use a copy of the latest development version, clone it using
Git_::

    $ git clone git://github.com/a-e/csvsee.git

then install as before using ``setup.py`` or ``pip``.

.. _downloads page: https://launchpad.net/csvsee/+download
.. _Git: http://git-scm.com/
.. _pip: http://pypi.python.org/pypi/pip
.. _Python: http://python.org/download/
.. _matplotlib: http://sourceforge.net/projects/matplotlib/files/matplotlib/matplotlib-0.99.1/
.. _NumPy: http://sourceforge.net/projects/numpy/files/



