csvgraph
--------

The ``csvgraph.py`` script in this folder is designed to generate graphs of
comma-separated (.csv) data files, particularly those created by the
Windows Performance Monitor tool.

Prerequisites:

  Python:
    http://www.python.org/download/
  Matplotlib:
    http://matplotlib.sourceforge.net/

You may want to copy the ``csvgraph.py`` script somewhere on your system path
for easier execution. Run the script without arguments to see usage notes.

At minimum, you need to provide:

  - The ``filename.csv`` containing your data
  - One column to use as the X-axis of the graph, typically a date/time field
  - One or more columns to plot on the Y-axis. All data must be integer or
    floating-point numeric values.

All column names can be specified as regular expressions that may match
one or more column headings in the .csv file. For example, if you have a file
called ``perfmon.csv`` with columns named like this:

  "Eastern Time","CPU (user)","CPU (system)","CPU (idle)"

You can generate a graph of user, system, and idle CPU values over time like this:

  csvgraph.py perfmon.csv "Eastern Time" "CPU.*"

By default, the X-axis is presumed to be a date/time value in this format:

  2009/01/13 15:30:05.123

You can specify alternative date/time formats using the ``-dateformat``
option. See http://docs.python.org/library/datetime.html for the valid
formatting operators. Use ``-dateformat ""`` if your X-axis is NOT a
date/time value.

