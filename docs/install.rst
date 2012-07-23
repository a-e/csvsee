Installation
============

You'll need Python_ before doing anything else. Most Linux distributions already
have this installed, but you can use this to check::

    $ which python
    /usr/bin/python

To use the graphing features of CSVSee, you'll need matplotlib_. On Ubuntu, this
should work::

    $ sudo apt-get install python-matplotlib

If you want to install an official release, first download one from the
`downloads page`_, and extract it somewhere.

Then, open that directory in a terminal and run::

    $ sudo python setup.py install

Or use pip_::

    $ sudo apt-get install python-pip
    $ sudo pip install .

One advantage of using ``pip`` is that you can uninstall later like so::

    $ sudo pip uninstall CSVSee

If you'd rather use a copy of the latest development version, clone it using
Git_::

    $ git clone git://github.com/a-e/csvsee.git

then install as before using ``setup.py`` or ``pip``.


Using virtualenv
----------------

There are some hassles when installing CSVSee's dependencies in a virtualenv_.
Specifically, NumPy_ and matplotlib_ must be compiled from source, requiring
extra development headers and other dependencies that are not easily installable
using pip_. For this reason, it's strongly recommended that you just install
NumPy and matplotlib through your regular package manager (like ``apt-get``).

If you really want to install them in a virtualenv, you could try this::

    $ sudo apt-get install python-dev libpng-dev

In order to display an interactive graphing window, you'll also need a GUI
backend that matplotlib can use. Qt4, Gtk, and Tkinter should all work. I use
Qt4::

    $ sudo apt-get install python-qt4

Then you may be able to do::

    $ pip install numpy
    $ pip install matplotlib

But I make no promises. In fact, I couldn't get it to work, so if you manage to
do so, please `open an issue`_ describing how you did it, so I can include it in
this documentation.

.. _virtualenv: http://www.virtualenv.org/en/latest/index.html
.. _downloads page: https://launchpad.net/csvsee/+download
.. _Git: http://git-scm.com/
.. _pip: http://pypi.python.org/pypi/pip
.. _Python: http://python.org/download/
.. _matplotlib: http://sourceforge.net/projects/matplotlib/files/matplotlib/matplotlib-0.99.1/
.. _NumPy: http://sourceforge.net/projects/numpy/files/
.. _open an issue: http://github.com/a-e/csvsee/issues

