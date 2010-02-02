#! /usr/bin/env python
# grindercsv.py

"""Generate a CSV summary report from Grinder log files.
"""

import os
import sys
import shlex
import csv
from glob import glob
from datetime import datetime

class NoTestNames (Exception):
    pass

class TestStats:
    """Statistics on all tests, as gathered from a Grinder data_* file.
    """
    _stats = (
        'Test time',
        'Errors',
        'Time to establish connection',
        'Time to first byte',
        'Time to resolve host',
        'HTTP response length',
        'HTTP response errors',
    )
    def __init__(self, grinder_outfile, *grinder_datafiles):
        self.outfile = grinder_outfile
        self.datafiles = grinder_datafiles
        # Get test (number, name) pairs
        self.tests = self.get_test_names()
        if not self.tests:
            raise NoTestNames("No test names found in '%s'" % self.outfile)
        # Number of iterations of each test that were run
        self.test_counts = {}
        # Accumulated statistics for each test
        self.test_totals = {}
        for test_num in self.tests:
            self.test_counts[test_num] = 0
            self.test_totals[test_num] = dict((stat, 0) for stat in self._stats)
        # Estimated start time for test run
        self.start = 0
        # Populate statistics
        self.populate_stats()


    def get_test_names(self):
        """Get a list of (number, name) for each test from the summary
        portion of the current outfile.
        """
        tests = []
        for line in open(self.outfile, 'r'):
            if line.startswith('Test '):
                fields = shlex.split(line)
                tests.append((fields[1], fields[-1]))
        return dict(tests)


    def populate_stats(self):
        """Return a list of TestStats, with accumulated statistics for all
        tests in the given Grinder output and data files.
        """
        for datafile in self.datafiles:
            print("Getting test stats from %s" % datafile)
            data = csv.DictReader(open(datafile, 'r'), skipinitialspace=True)
            for row in data:
                self.add(row)


    def add(self, row):
        """Add a row from a data_* file to the stats.
        """
        test_num = row['Test']

        # Don't add if this row if it's for an unknown test number
        if test_num not in self.test_counts:
            return

        # If start time is not yet set, set it now
        if self.start == 0:
            timestamp = float(row['Start time (ms since Epoch)'])/1000
            self.start = datetime.utcfromtimestamp(timestamp)

        # Accumulate each statistic
        for stat in self._stats:
            self.test_totals[test_num][stat] += int(row[stat])

        self.test_counts[test_num] += 1


    def csv_heading(self):
        """Return a list of heading strings for all tests.
        """
        heading = ['GMT']
        for (test_num, test_name) in sorted(self.tests.items()):
            for stat in self._stats:
                heading.append('%s - %s' % (stat, test_name))
        return heading


    def csv_row(self):
        """Return a list of values for all tests, corresponding to headings.
        """
        timestamp = datetime.strftime(self.start, '%m/%d/%Y %H:%M:%S') + '.000'
        row = [timestamp]
        for (test_num, test_name) in sorted(self.tests.items()):
            total = self.test_totals[test_num]
            count = self.test_counts[test_num]
            # Some totals should be averaged by dividing by count;
            # others actually make sense as a total
            row.extend([
                str(total['Test time'] / count),
                str(total['Errors']),
                str(total['Time to establish connection'] / count),
                str(total['Time to first byte'] / count),
                str(total['Time to resolve host'] / count),
                str(total['HTTP response length'] / count),
                str(total['HTTP response errors']),
            ])
        return row

    def __str__(self):
        result = "TestStats(%s, %s)\n" % (self.outfile, ', '.join(self.datafiles))
        result += "  start: %s" % self.start
        return result

    def __lt__(self, other):
        return self.start < other.start

    def __eq__(self, other):
        return self.start == other.start

    def __gt__(self, other):
        return self.start > other.start


def grinder_files(include_dirs):
    """Return a list of full pathnames to all out_* and data_* files
    found in descendants of include_dirs.
    """
    out_data_files = []
    for dirname in include_dirs:
        if not os.path.exists(dirname):
            raise ValueError("No such directory: %s" % dirname)
        for (path, dirs, files) in os.walk(dirname):
            outfiles = glob(os.path.join(path, 'out_*.log'))
            datafiles = glob(os.path.join(path, 'data_*.log'))
            if outfiles and datafiles:
                out_data_files.append((outfiles[0], datafiles))
    return out_data_files


def full_csv_summary(include_dirs, csv_file):
    """Generate a full CSV summary of all grinder out_* and data_* files
    in descendants of the current directory.
    """
    stats = []
    for (out, data) in grinder_files(include_dirs):
        try:
            stat = TestStats(out, *data)
        except NoTestNames:
            print("No test names found in '%s', skipping..." % out)
        else:
            stats.append(stat)
    if not stats:
        print("No grinder out_* and data_* files found.")
        return

    # Sort stats by start time
    stats = sorted(stats)

    # Open the CSV file for writing
    csv_output = open(csv_file, 'w')

    def writeline(items):
        csv_output.write('"%s"\n' % '","'.join(items))

    # Get a heading that will be used for the CSV file
    heading = stats[0].csv_heading()
    writeline(heading)
    for stat in stats:
        if stat.csv_heading() == heading:
            writeline(stat.csv_row())
        else:
            print("CSV heading from %s doesn't match, skipping..." % stat.outfile)

    csv_output.close()


# Main program
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: grindercsv.py [dirnames] <csv_outfile>")
        sys.exit()
    else:
        include_dirs = sys.argv[1:-1]
        csv_outfile = sys.argv[-1]

    if not csv_outfile.endswith('.csv'):
        print("Last argument needs to be a filename ending in .csv.")
        sys.exit()

    full_csv_summary(include_dirs, csv_outfile)


