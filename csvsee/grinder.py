# grinder.py

"""Tools for working with Grinder log output and generating CSV data.
"""

"""Generate a CSV summary report from Grinder log files.

Grinder's data_* files store timestamps as milliseconds. It seems unlikely that
a typical stress test will need this kind of resolution; a reasonable minimum
resolution might be seconds (timestamp / 1000). To create 1-second "bins" with
accumulated statistics, it should work to index each bin by its timestamp in
seconds:

    datetime.utcfromtimestamp(seconds_since_epoch)

How to create larger bins? Well, if we only need minute-resolution, it should
work to simply truncate the seconds down to the nearest minute. A crude way
to do this:

    timestamp = (timestamp / 60) * 60

This only works for integer values of timestamp, so I should ensure that all
timestamps are converted to integers first.

What's in a bin? Well, it should be a summation of all the data that falls
within that time interval. Simply truncating the timestamp will give us the
right bin index, but within that bin, we will want to track each test number
separately. The question is whether to divide first by test number, then
allocate bins for each test, or divide into bins and then subdivide by test
number. I think it makes more sense for each test to have multiple bins, than
for each bin to have multiple tests.

Furthermore, each test may span across multiple data files. Generally, we'll
want to accumulate bin data across all data files.

Let's say we have a Test class that keeps track of all statistics on
a given test (including test number and name, and all bins of data). We can
keep a dictionary of Tests indexed by test number--then, when parsing
data files, for each row, we'll look up the test number, then send the row
of data to the relevant Test object, which will accumulate data in bins.

What will the ultimate .csv output look like then? It would be nice if each
test could get its own column(s), for compatibility with csvgraph.py.
Perhaps it makes sense to generate one .csv for response time, another for
errors, another for response length, etc.

Construct the header row by iterating across all test names, in order of
test number. GMT goes in the first column.

Then, iterate across the range of timestamps (this will necessitate remembering
the min/max timestamp seen in all data files). Within that iteration, iterate
across the tests and fetch data from the relevant timestamped bin. If a given
test has nothing in that bin (i.e. that bin doesn't exist), then output a 0 or
null value.

Alright, so each bin has a resolution. This implies that each Test has a
"bin resolution", and by extension the entire report-generator has the same
resolution. In fact, a bin itself doesn't need to care about its own resolution
(or even its own timestamp)--it only needs to be responsible for accumulating
statistics, and counting the number of accumulations done so far.

"""

import os
import sys
import shlex
import csv
from glob import glob
from datetime import datetime


def get_test_names(outfile):
    """Return a dict of ``{number: name}`` for each test from the summary
    portion of the given Grinder ``out*`` file.
    """
    tests = {}
    for line in open(outfile, 'r'):
        if line.startswith('Test '):
            fields = shlex.split(line)
            number, name = int(fields[1]), fields[-1]
            tests[number] = name
    return tests


class NoTestNames (Exception):
    """Failure to find any test names in a Grinder ``out*`` file.
    """
    pass


class Bin:
    """Accumulated statistics for an interval of time.
    """
    def __init__(self, stat_names):
        """Create a bin for accumulating the given statistics.

            >>> b = Bin(['Errors', 'HTTP response length', 'Test time'])

        """
        self.stats = dict((stat, 0) for stat in stat_names)
        self.count = 0


    def add(self, row):
        """Accumulate a row of statistics in this bin.
        All statistics are accumulated as integers.
        """
        for stat in self.stats:
            self.stats[stat] += int(row[stat])
        self.count += 1


    def average(self, stat):
        """Return the integer average (mean) of the given statistic.
        """
        if self.count > 0:
            return (self.stats[stat] / self.count)
        else:
            return 0


class Test:
    """Statistics for a single Test in a Grinder test run.
    """
    # Statistics to sum
    sum_stats = [
        'Errors',
        'HTTP response errors',
    ]
    # Statistics to average
    average_stats = [
        'HTTP response length',
        'Test time',
        # May need these, or may not...
        #'Time to establish connection',
        #'Time to first byte',
        #'Time to resolve host',
    ]
    all_stats = sum_stats + average_stats


    def __init__(self, number, name, resolution=1):
        """Create a Test with the given number and name, and a resolution in
        seconds.
        """
        self.number = number
        self.name = name
        self.resolution = resolution
        # Bins of accumulated statistics, indexed by timestamp in seconds
        self.bins = {}


    def add(self, row):
        """Add a row of statistics for this test.
        """
        # Convert timestamp to seconds
        timestamp  = int(row['Start time (ms since Epoch)']) / 1000
        # Truncate the timestamp to the current resolution
        if self.resolution > 1:
            timestamp = (timestamp / self.resolution) * self.resolution
        # If a bin doesn't exist for this timestamp, create one
        if timestamp not in self.bins:
            self.bins[timestamp] = Bin(Test.all_stats)
        # Accumulate stats
        self.bins[timestamp].add(row)


    def timestamp_range(self):
        """Return the ``(start, end)`` timestamps for this test.
        """
        if not self.bins:
            return (0, 0)
        timestamps = sorted(self.bins.keys())
        return (min(timestamps), max(timestamps))


    def stat_at_time(self, stat, timestamp):
        """Return a statistic at the given timestamp (either sum or average).
        Return ``0`` if there is no data at the given time.
        """
        if timestamp not in self.bins:
            return 0
        # Get the appropriate bin
        bin = self.bins[timestamp]
        # For summed stats, just return the total
        if stat in Test.sum_stats:
            return bin.stats[stat]
        # For averaged stats, divide by count
        elif stat in Test.average_stats:
            return (bin.stats[stat] / bin.count)
        else:
            raise ValueError("Unknown stat: %s" % stat)


    def __str__(self):
        return "%s: %s" % (self.number, self.name)


class Report:
    """A report of statistics for a Grinder test run.
    """
    def __init__(self, resolution, grinder_outfile, *grinder_datafiles):
        self.resolution = resolution
        self.outfile = grinder_outfile
        self.datafiles = grinder_datafiles
        self.tests = {}
        self.populate_stats()


    def populate_stats(self):
        """Add statistics for all tests in all Grinder data files.
        """
        # Get test (number, name) pairs
        for (number, name) in get_test_names(self.outfile).iteritems():
            self.tests[number] = Test(number, name, self.resolution)

        if not self.tests:
            raise NoTestNames("No test names found in '%s'" % self.outfile)

        for datafile in self.datafiles:
            print("Getting test stats from %s" % datafile)
            data = csv.DictReader(open(datafile, 'r'), skipinitialspace=True)
            for row in data:
                self.add(row)


    def add(self, row):
        """Add a row from a ``data*`` file to the stats.
        """
        test_num = int(row['Test'])
        # Get the Test for this test number
        try:
            test = self.tests[test_num]
        # If this is an unknown test number, ignore it
        except KeyError:
            pass
        # Otherwise, add the row to the test stats
        else:
            test.add(row)


    def timestamp_range(self):
        """Return the ``(start, end)`` timestamps for this report, based
        on the timestamps of all tests within it.
        """
        # Get all (start, end) ranges from the tests
        ranges = [test.timestamp_range() for test in self.tests.values()]
        # Using list() here to future-proof
        start_times, end_times = list(zip(*ranges))
        return (min(start_times), max(end_times))


    def write_csv(self, stat, filename):
        """Write the given statistic for all tests to ``filename``.
        """
        # Open the CSV file for writing
        csv_writer = csv.writer(open(filename, 'w'))

        # Test number determines the order of columns
        test_numbers = sorted(self.tests.keys())

        # OOCalc has a hard limit of 65535 characters in a single line of a
        # .csv file. Figure out where to truncate the test names so they will
        # all fit in the header row.
        trunc_length = 65000 / len(test_numbers)

        # Assemble the header row
        header = ['GMT']
        # Sort by test number
        for test_num in test_numbers:
            trunc_name = str(self.tests[test_num])[:trunc_length]
            #header.append(str(test_num))
            header.append(trunc_name)
        # Write the header row
        csv_writer.writerow(header)

        # Assemble and write each row, sorted by timestamp
        start_time, end_time = self.timestamp_range()
        this_time = start_time
        while this_time <= end_time:
            timestamp = datetime.utcfromtimestamp(this_time)
            timestamp = datetime.strftime(timestamp, '%m/%d/%Y %H:%M:%S') + '.000'
            row = [timestamp]
            for test_num in test_numbers:
                row.append(self.tests[test_num].stat_at_time(stat, this_time))
            # Write the row
            csv_writer.writerow(row)
            # Step to the next timestamp
            this_time += self.resolution


def grinder_files(include_dir):
    """Return a list of full pathnames to all ``out*`` and ``data*`` files
    found in descendants of ``include_dir``.
    """
    if not os.path.exists(include_dir):
        raise ValueError("No such directory: %s" % include_dir)

    out_data_files = []
    for (path, dirs, files) in os.walk(include_dir):
        outfiles = glob(os.path.join(path, 'out_*.log'))
        datafiles = glob(os.path.join(path, 'data_*.log'))
        if outfiles and datafiles:
            out_data_files.append((outfiles[0], datafiles))

    return out_data_files



