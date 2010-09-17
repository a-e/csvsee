csvs
====

``csvs`` is the primary frontend for CSVSee. You can run this without arguments
to see what it expects. At minimum, you'll need to provide the name of a
command. Currently, two commands are implemented:

* ``csvs graph``: Generate graphs from ``.csv`` files
* ``csvs grep``: Search in text files and generate a ``.csv`` file
* ``csvs grinder``: Create ``.csv`` reports based on Grinder_ output file


csvs graph
----------

The ``graph`` command is designed to generate graphs of comma-separated (.csv)
data files. It was originally designed for graphing data from the Windows
Performance Monitor tool, but it can also be used more generally to graph any
CSV data that includes timestamps.

The only thing you must provide is a ``filename.csv`` containing your data. By
default, the first column of data is used as the X-coordinate; if it's a
timestamp, its format will be guessed.

You can optionally specify one or more regular expressions to match the column
names you want to graph. If you don't provide these, all columns will be
graphed. All data must be integer or floating-point numeric values; anything
that isn't a date or number will be plotted as a 0.

Column names can be specified as regular expressions that may match one or more
column headings in the .csv file. For example, if you have a file called
``perfmon.csv`` with columns named like this::

    "Eastern Time","CPU (user)","CPU (system)","CPU (idle)","Memory"

You can generate a graph of user, system, and idle CPU values over time like
this::

    csvs graph perfmon.csv "CPU.*"

Run ``csvs graph`` without arguments to see full usage notes.


csvs grep
---------

The ``grep`` command generates a ``.csv`` file by matching strings in one or
more timestamped log files. It would typically be used to generate a report of
how frequently certain messages or errors appear through time.

For example, if you have ``parrot.log`` containing::

    2010/08/30 13:57:14 Pushing up the daisies
    2010/08/30 13:58:08 Stunned
    2010/08/30 13:58:11 Stunned
    2010/08/30 14:04:22 Pining for the fjords
    2010/08/30 14:05:37 Pushing up the daisies
    2010/08/30 14:09:48 Pining for the fjords

And you wanted to see how often each of these phrases occur, do::

    csvs grep parrot.log \
        -match "Stunned" "Pushing up the daisies" "Pining for the fjords" \
        -out parrot.csv

By default, the ``grep`` command counts the number of occurrences each minute,
so this would give you a ``.csv`` file looking something like this (whitespace
added for readability)::

    "Timestamp",        "Stunned", "Pushing up the daisies", "Pining for the fjords"
    2010/08/30 13:57,   0,         1,                        0
    2010/08/30 13:58,   2,         0,                        0
    2010/08/30 14:04,   0,         0,                        1
    2010/08/30 14:05,   0,         1,                        0
    2010/08/30 14:09,   0,         0,                        1

You can change the resolution using the ``-seconds`` option. For example, to
count the occurrences each hour, use ``-seconds 3600``.

Run ``csvs grep`` without arguments to see full usage notes.


csvs grinder
------------

The ``grinder`` command generates ``.csv`` files from Grinder_ logs. You must
provide the name of a ``out*`` file, and one or more ``data*`` files generated
from the same test run::

    csvs grinder out-0.log data-*.log foo

This will write four ``.csv`` files in the current directory:

* ``foo_Errors.csv``
* ``foo_HTTP_response_errors.csv``
* ``foo_HTTP_response_length.csv``
* ``foo_Test_time.csv``

By default, statistics are summarized with a 60-second resolution; that is, all
statistics within each 60-second interval are summed (in the case of errors) or
averaged (in the case of response length and test time). To change the interval
resolution, pass the ``-seconds`` option. For instance, to summarize statistics
in 10-minute intervals::

    csvs grinder -seconds 600 out-0.log data-*.log foo

Run ``csvs grinder`` without arguments to see full usage notes.

.. _Grinder: http://grinder.sourceforge.net/

