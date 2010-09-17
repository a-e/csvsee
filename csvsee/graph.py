# graph.py

"""Provides a `Graph` class for creating graphs from ``.csv`` data files.
"""

import sys
import csv
from datetime import datetime, timedelta

from csvsee import utils, dates
import pylab
import matplotlib as mpl


class Graph (object):
    """A graph of data from a CSV file.
    """
    # Graph configuration setting types
    strings = [
        'x',
        'dateformat',
        'title',
        'linestyle',
        'xlabel',
        'ylabel',
    ]
    ints = [
        'gmtoffset',
        'truncate',
        'top',
        'drop',
        'peak',
    ]
    floats = [
        'ymax',
    ]
    bools = [
        'zerotime',
    ]

    def __init__(self, csv_file, **kwargs):
        """Create a graph from data in ``csv_file``.
        """
        self.csv_file = csv_file

        # Default configuration
        self.config = {
            'x': '',
            'y': ['.*'],
            'title': csv_file,
            'xlabel': '',
            'ylabel': '',
            'ymax': 0,
            'truncate': 0,
            'top': 0,
            'peak': 0,
            'drop': 0,
            'zerotime': False,
            'linestyle': '',
            'dateformat': 'guess',
            'gmtoffset': 0,
        }
        # Update default configuration with keyword args
        self.config.update(kwargs)

        # These will be set by generate()
        self.figure = None
        self.figtitle = None
        self.axes = None
        self.legend = None


    def __getitem__(self, name):
        """Get the configuration setting with the given ``name``.
        """
        return self.config[name]


    def __setitem__(self, name, value):
        """Set the configuration setting ``name`` to ``value``.
        """
        self.config[name] = value


    def guess_date_format(self, date_column):
        """Try to guess the date format used in the current ``.csv`` file, by
        reading from the first row of the ``date_column`` column.
        """
        infile = open(self.csv_file, 'r')
        reader = csv.DictReader(infile)
        row = reader.next()
        infile.close()
        # Return the guessed format
        return dates.guess_date_format(row[date_column])


    def generate(self):
        """Generate the graph.
        """

        print("Reading '%s'" % self.csv_file)
        reader = csv.DictReader(open(self.csv_file, 'r'))

        # Attempt to match column names
        x_column, y_columns = utils.matching_xy_fields(
            self['x'], self['y'], reader.fieldnames)

        # Do we need to guess what format the date is in?
        if self['dateformat'] == 'guess':
            self['dateformat'] = self.guess_date_format(x_column)

        # Read each row in the .csv file and populate x and y value lists
        x_values, y_values = utils.read_xy_values(reader,
            x_column, y_columns, self['dateformat'], self['gmtoffset'], self['zerotime'])

        # Create the figure and plot
        self.figure = pylab.figure()
        self.axes = self.figure.add_subplot(111)
        self.axes.grid(True)

        # Label X-axis with provided label, or column name
        self.axes.set_xlabel(self['xlabel'] or x_column)

        # Add graph title if provided
        if self['title']:
            self.figtitle = self.figure.suptitle(self['title'], fontsize=18)

        # Do date formatting of axis labels if the X column is a date field
        if self['dateformat']:
            self.add_date_labels(min(x_values), max(x_values))
            self.figure.autofmt_xdate()

        # Get the top n by average?
        if self['top']:
            y_columns = utils.top_by_average(self['top'], y_columns, y_values, self['drop'])
            print("********** Top %d columns by average:" % self['top'])
            print('\n'.join(y_columns))
        # Get the top n by peak?
        elif self['peak']:
            y_columns = utils.top_by_peak(self['peak'], y_columns, y_values, self['drop'])
            print("********** Top %d columns by peak:" % self['peak'])
            print('\n'.join(y_columns))

        # Plot lines for all Y columns
        lines = []
        for y_col in y_columns:
            line = self.axes.plot(x_values, y_values[y_col], self['linestyle'])
            lines.append(line)

        # Set Y-limit if provided
        if self['ymax'] > 0:
            print("Setting ymax to %s" % self['ymax'])
            self.axes.set_ylim(0, self['ymax'])

        # Draw a legend for the figure
        # If a Y label was given, use that; otherwise, strip
        # common prefix from labels, and use that as the Y label
        if self['ylabel']:
            labels = [col for col in y_columns]
            self.axes.set_ylabel(self['ylabel'])
        else:
            prefix, labels = utils.strip_prefix(y_columns)
            self.axes.set_ylabel(prefix)

        # Truncate labels if desired
        if self['truncate'] > 0:
            labels = [label[0:self['truncate']] for label in labels]

        self.legend = pylab.legend(lines, labels,
            loc='upper center', bbox_to_anchor=(0.5, -0.15),
            prop={'size': 9}, ncol=3)


    def add_date_labels(self, min_date, max_date):
        """Add date labels to the graph.
        """
        self.axes.set_xlim(min_date, max_date)
        locator = mpl.dates.AutoDateLocator()
        locator.set_axis(self.axes.xaxis)
        formatter = mpl.dates.AutoDateFormatter(locator)
        self.axes.xaxis.set_major_locator(locator)
        self.axes.xaxis.set_major_formatter(formatter)


    def save(self, filename):
        """Save the graph to ``filename``. The format is determined by the
        extension of ``filename``; if it's not ``png``, ``svg``, or ``pdf``,
        then a `ValueError` is raised.
        """
        ext = filename[-3:]
        if ext not in ('png', 'svg', 'pdf'):
            raise ValueError("File extension must be 'png', 'svg', or 'pdf'."
                             " Got '%s' instead." % ext)

        # Ensure that title and legend don't get cropped out
        extra = [
            self.legend.legendPatch,
            self.figtitle,
        ]
        self.figure.savefig(
            filename,
            format=ext,
            bbox_inches='tight',
            bbox_extra_artists=extra)
        print("Saved '%s' in '%s' format." % (filename, ext))


    def show(self):
        """Display the graph in a GUI window.
        """
        pylab.show()


