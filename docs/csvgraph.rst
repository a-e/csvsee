:mod:`csvgraph`
===============

The ``csvgraph.py`` script is designed to generate graphs of comma-separated
(.csv) data files. It was originally designed for graphing data from the
Windows Performance Monitor tool, but it can also be used more generally to
graph any CSV data that includes timestamps.

You may want to copy the ``csvgraph.py`` script somewhere on your system path
for easier execution. Run the script without arguments to see usage notes.

The only thing you must provide is a ``filename.csv`` containing your data.
By default, the first column of data is used as the X-coordinate; if it's
a timestamp, its format will be guessed.

You can optionally specify one or more regular expressions to match the
column names you want to graph. If you don't provide these, all columns
will be graphed. All data must be integer or floating-point numeric values;
anything that isn't a date or number will be plotted as a 0.

Column names can be specified as regular expressions that may match one or more
column headings in the .csv file. For example, if you have a file called
``perfmon.csv`` with columns named like this::

  "Eastern Time","CPU (user)","CPU (system)","CPU (idle)"

You can generate a graph of user, system, and idle CPU values over time like
this::

  csvgraph.py perfmon.csv "Eastern Time" "CPU.*"

By default, the X-axis is presumed to be a date/time value in this format::

  2009/01/13 15:30:05.123

You can specify alternative date/time formats using the ``-dateformat``
option. See the datetime_ documentation for valid formatting operators. Use
``-dateformat ""`` if your X-axis is NOT a date/time value.

.. _datetime: http://docs.python.org/library/datetime.html


Usage
-----
.. automodule:: csvgraph

