#! /usr/bin/env python
# csvgraph.py

__doc__ = """Generage graphs from .csv data files.

Usage::

    csvgraph.py filename.csv [-options] "X column" "Y column 1" ["Y column 2"] ...

Where filename.csv contains comma-separated values, with column names in the
first row, and all subsequent arguments are regular expressions that may match
one or more column names.

Options:

    -title "Title"
        Set the title label for the graph. Default: No title.

    -save "filename.(png|svg|pdf)"
        Save the graph to a file. Default: Show the graph in a viewer.

    -dateformat "<format string>"
        Interpret the X-column as a date in the given format. Examples:
            %m/%d/%y %I:%M:%S %p: 12/10/09 3:45:56 PM (Grinder logs)
            %m/%d/%Y %H:%M:%S.%f: 12/10/2009 15:45:56.789 (Perfmon)
        See http://docs.python.org/library/datetime.html for valid formats.
        The Perfmon date format is the default. If the X-column
        is NOT a date, use -dateformat ""

    -linestyle "<format string>"
        Define the style of lines plotted on the graph. Examples are:
            "-"  Solid line (Default)
            "."  Point marker
            "o"  Circle marker
            "o-" Circle + solid lines
        See the Matplotlib Axes.plot documentation for available styles:
        http://matplotlib.sourceforge.net/api/axes_api.html#matplotlib.axes.Axes.plot

    -gmt [+/-]<hours>
        Adjust timestamps if they are not in GMT. For example, if the
        timestamps are GMT-6, use -gmt +6 to make the graph display them
        as GMT times.

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

At least one X-column and one Y-column must be provided; if any Y-column
expression matches multiple column names, and/or if multiple Y-column
expressions are provided, then all matching columns will be included in the
graph.

If the X-column is a date field, then the X axis will be displayed in HH:MM
format. Otherwise, all columns must be numeric (integer or floating-point).
"""
usage = __doc__

"""TODO
"""

import sys

from csvsee.utils import print_columns
from csvsee.graph import Graph


def usage_error(message):
    """Print a usage error, along with a custom message, then exit.
    """
    print(usage)
    print('*** %s' % message)
    sys.exit(1)


# Main program
if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1].lower().endswith('.csv'):
        print_columns(sys.argv[1])
        sys.exit()
    elif len(sys.argv) < 4:
        usage_error("Need a .csv filename and at least two column names")
    else:
        args = sys.argv[1:]

    save_file = ''

    # CSV file is always the first argument
    csv_file = args.pop(0)
    if not csv_file.lower().endswith('.csv'):
        usage_error("First argument must be a filename with .csv extension.")

    # Create Graph, using Perfmon date format by default
    graph = Graph(csv_file, date_format='%m/%d/%Y %H:%M:%S.%f')

    # Get any -options that follow
    while args[0].startswith('-'):
        opt = args.pop(0)
        if opt == '-title':
            graph.title = args.pop(0)

        elif opt == '-save':
            save_file = args.pop(0)

        elif opt == '-dateformat':
            graph.date_format = args.pop(0)

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

        else:
            usage_error("Unknown option: %s" % opt)

    # Get positional arguments
    graph.x_expr = args.pop(0)
    graph.y_exprs = args

    # Generate the graph
    graph.generate()
    if save_file:
        graph.save(save_file)
    else:
        graph.show()

