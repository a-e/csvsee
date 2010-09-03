#! /usr/bin/env python
# csvgraph.py

__doc__ = """Generage graphs from .csv data files.

Usage::

    csvgraph.py filename.csv [-options] ["Column 1"] ["Column 2"] ...

Where filename.csv contains comma-separated values, with column names in the
first row, and all subsequent arguments are regular expressions that may match
one or more column names.

Options:

    -datetime "<column name>"
        The name of the column containing your timestamp. If this is
        omitted, the first column of the .csv file is assumed to be
        the timestamp. The timestamp column determines the X-axis, and
        will not be graphed (even if it matches a column expression).

    -dateformat "<format string>"
        Interpret the timestamp as a date in the given format. Examples:
            %m/%d/%y %I:%M:%S %p: 12/10/09 3:45:56 PM (Grinder logs)
            %m/%d/%Y %H:%M:%S.%f: 12/10/2009 15:45:56.789 (Perfmon)
        See http://docs.python.org/library/datetime.html for valid formats.
        By default, the date format will be guessed based on the first row of
        the .csv file. If the X-column is NOT a date, use -dateformat ""

    -title "Title"
        Set the title label for the graph. By default, the .csv filename
        is used as the graph title.

    -save "filename.(png|svg|pdf)"
        Save the graph to a file. Default is to show the graph in a viewer.

    -linestyle "<format string>"
        Define the style of lines plotted on the graph. Examples are:
            "-"  Solid line (Default)
            "."  Point marker
            "o"  Circle marker
            "o-" Circle + solid lines
        See the Matplotlib Axes.plot documentation for available styles:
        http://matplotlib.sourceforge.net/api/axes_api.html#matplotlib.axes.Axes.plot

    -xlabel "Label string"
        Use the given string as the label of the X axis. If omitted, the
        name of the X-column is used.

    -ylabel "Label string"
        Use the given string as the label of the Y axis. If omitted, the
        prefix common to all the given column names is used.

    -ymax <number>
        Set the maximum Y-value beyond which the graph is cropped. By default,
        maximum Y-value is determined by the maximum value present in the data.

    -truncate <number>
        Truncate the column labels to <number> characters. By default,
        no truncation is done.

    -top <number>
        Graph only the top <number> columns, based on the average of
        all values in matching columns.

    -peak <number>
        Graph only the top <number> columns, based on the highest peak
        value in matching columns.

    -gmt [+/-]<hours>
        Adjust timestamps if they are not in GMT. For example, if the
        timestamps are GMT-6, use -gmt +6 to make the graph display them
        as GMT times.

    -zerotime
        Adjust all timestamps so the graph starts at 00:00.

If no column names are given, then all columns are graphed. To graph only
specific columns, provide one or more column expressions after the .csv
filename and any options. Column names are given as regular expressions,
allowing you to match multiple columns.

Examples:

    csvgraph.py data.csv
        Graph all columns found in data.csv, using the first column
        as the X-axis.

    csvgraph.py data.csv -top 5
        Graph the 5 columns with the highest average value

    csvgraph.py data.csv "^Response.*"
        Graph all columns beginning with the word "Response"

    csvgraph.py data.csv A B C
        Graph columns "A", "B", and "C". Note that these are regular
        expressions, and will actually match all columns containing "A", all
        columns containing "B", and all columns containing "C".

If the first column is a date field, then the X axis will be displayed in HH:MM
format. Otherwise, all columns must be numeric (integer or floating-point).
"""
usage = __doc__

"""TODO
"""

import sys

from csvsee.graph import Graph


def usage_error(message):
    """Print a usage error, along with a custom message, then exit.
    """
    print(usage)
    print('*** %s' % message)
    sys.exit(1)


# Main program
if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage_error("Please provide the name of a .csv file.")
    else:
        args = sys.argv[1:]

    # CSV file is always the first argument
    csv_file = args.pop(0)
    if not csv_file.lower().endswith('.csv'):
        usage_error("First argument must be a filename with .csv extension.")

    # Create Graph for this csv file
    graph = Graph(csv_file)

    save_file = ''

    # Get any -options that follow
    while args and args[0].startswith('-'):
        opt = args.pop(0)
        if opt == '-datetime':
            graph.x_expr = args.pop(0)

        elif opt == '-dateformat':
            graph.date_format = args.pop(0)

        elif opt == '-title':
            graph.title = args.pop(0)

        elif opt == '-save':
            save_file = args.pop(0)

        elif opt == '-linestyle':
            graph.line_style = args.pop(0)

        elif opt == '-gmt':
            graph.gmt_offset = int(args.pop(0))

        elif opt == '-xlabel':
            graph.xlabel = args.pop(0)

        elif opt == '-ylabel':
            graph.ylabel = args.pop(0)

        elif opt == '-ymax':
            graph.ymax = float(args.pop(0))

        elif opt == '-truncate':
            graph.truncate = int(args.pop(0))

        elif opt == '-top':
            graph.top = int(args.pop(0))

        elif opt == '-peak':
            graph.peak = int(args.pop(0))

        elif opt == '-zerotime':
            graph.zero_time = True

        else:
            usage_error("Unknown option: %s" % opt)

    # Get column expressions (all remaining arguments, if any)
    if args:
        graph.y_exprs = args

    # Generate the graph
    graph.generate()
    if save_file:
        graph.save(save_file)
    else:
        graph.show()

