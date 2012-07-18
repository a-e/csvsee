# test_grinder.py

"""Unit tests for the `csvsee.grinder` module.
"""

import os
import csv
import unittest
from csvsee import grinder
from . import basic_dir, data_dir, temp_filename

class TestGrinder (unittest.TestCase):
    def test_get_test_names(self):
        """Test the `get_test_names` function.
        """
        expect = {
            1000: 'First page',
            1001: 'First test',
            1002: 'Second test',
            1003: 'Third test',
            1004: 'Fourth test',
            1005: 'Fifth test',
            1006: 'Sixth test',
        }
        # Works with an out*.log containing a summary
        outfile = os.path.join(basic_dir, 'out_XP-0.log')
        self.assertEqual(grinder.get_test_names(outfile), expect)
        # Works with an out*.log having no summary, but
        # having grinder-webtest "------ Test <num>: Description"
        outfile = os.path.join(data_dir, 'webtest', 'out_webtest-0.log')
        self.assertEqual(grinder.get_test_names(outfile), expect)


    def test_Bin(self):
        """Test the `Bin` class.
        """
        bin = grinder.Bin(['Errors', 'Test time'])
        # Empty bin
        self.assertEqual(bin.count, 0)
        self.assertEqual(bin.average('Errors'), 0)


    def test_Test(self):
        """Test the `Test` class.
        """
        tst = grinder.Test(101, 'Foobared', 30)
        self.assertEqual(tst.number, 101)
        self.assertEqual(tst.name, 'Foobared')
        self.assertEqual(tst.resolution, 30)
        self.assertEqual(tst.timestamp_range(), (0, 0))


    def test_empty_Report(self):
        """Test the `Report` class with an out* file having no test names
        (that is, a file that's either not a Grinder out* file, or one that
        hasn't finished writing test names to the end).
        """
        outfile = os.path.join(data_dir, 'incomplete', 'incomplete.log')
        self.assertRaises(grinder.NoTestNames,
                          grinder.Report, 60, outfile)



    def test_grinder_files(self):
        """Test the `grinder_files` function.
        """
        # Expected out* and data* filenames
        outfile = os.path.join(basic_dir, 'out_XP-0.log')
        data0 = os.path.join(basic_dir, 'data_XP-0.log')
        data1 = os.path.join(basic_dir, 'data_XP-1.log')

        self.assertEqual(grinder.grinder_files(basic_dir), [
            (outfile, [data0, data1])
        ])

        # Exception on nonexistent directory
        self.assertRaises(ValueError, grinder.grinder_files, 'f00b4r')


class TestGrinderReport (unittest.TestCase):
    def setUp(self):
        self.outfile = os.path.join(basic_dir, 'out_XP-0.log')
        self.data0 = os.path.join(basic_dir, 'data_XP-0.log')
        self.data1 = os.path.join(basic_dir, 'data_XP-1.log')

    def test_resolution(self):
        report = grinder.Report(60, self.outfile, self.data0, self.data1)
        self.assertEqual(report.resolution, 60)

    def test_timestamp_ranges(self):
        report = grinder.Report(60, self.outfile, self.data0, self.data1)
        # Timestamp ranges for each test number
        test_timestamp_ranges = [
            (1001, 1283195400, 1283195760),
            (1002, 1283195400, 1283195760),
            (1003, 1283195400, 1283195760),
            (1004, 1283195400, 1283195760),
            (1005, 1283195460, 1283195820),
            (1006, 1283195460, 1283195820),
        ]
        for (test_number, start, end) in test_timestamp_ranges:
            self.assertEqual(
                report.tests[test_number].timestamp_range(), (start, end))
        # Overall timestamp range
        self.assertEqual(report.timestamp_range(), (1283195400, 1283195820))

    def test_write_csv(self):
        """Test the `Report` class.
        """
        report = grinder.Report(60, self.outfile, self.data0, self.data1)

        # Writing report to a .csv file
        report_csv = temp_filename('csv')
        report.write_csv('Test time', report_csv)
        # Ensure data matches what's expected
        lines = [line.rstrip() for line in open(report_csv)]
        self.assertEqual(lines, [
            'GMT,1001: First test,1002: Second test,1003: Third test,1004: Fourth test,1005: Fifth test,1006: Sixth test',
            '08/30/2010 19:10:00.000,1546,318,2557,35882,0,0',
            '08/30/2010 19:11:00.000,0,0,0,0,1883,2333',
            '08/30/2010 19:12:00.000,0,0,0,0,0,0',
            '08/30/2010 19:13:00.000,0,0,0,0,0,0',
            '08/30/2010 19:14:00.000,0,0,0,0,0,0',
            '08/30/2010 19:15:00.000,0,0,0,0,0,0',
            '08/30/2010 19:16:00.000,1270,322,2196,33988,2054,2411',
            '08/30/2010 19:17:00.000,0,0,0,0,2080,2848'
        ])

        # Remove temporary file
        os.unlink(report_csv)


class TestGrinderTest (unittest.TestCase):
    def setUp(self):
        data0 = os.path.join(basic_dir, 'data_XP-0.log')
        data1 = os.path.join(basic_dir, 'data_XP-1.log')
        self.test = grinder.Test(1006, 'Sixth test', 60)
        for filename in [data0, data1]:
            for row in csv.DictReader(open(filename, 'r'), skipinitialspace=True):
                if int(row['Test']) == 1006:
                    self.test.add(row)

    def test_init(self):
        pass

    def test_add(self):
        pass

    def test_timestamp_range(self):
        self.assertEqual(self.test.timestamp_range(), (1283195460, 1283195820))

    def test_stat_at_time_averaged(self):
        self.assertEqual(self.test.stat_at_time('Test time', 1283195460), 2333)
        self.assertEqual(self.test.stat_at_time('Test time', 1283195760), 2411)
        self.assertEqual(self.test.stat_at_time('Test time', 1283195820), 2848)

    def test_stat_at_time_summed(self):
        self.assertEqual(self.test.stat_at_time('Errors', 1283195460), 0)
        self.assertEqual(self.test.stat_at_time('Errors', 1283195760), 0)
        self.assertEqual(self.test.stat_at_time('Errors', 1283195820), 0)

    def test_stat_at_time_tx_counts(self):
        self.assertEqual(self.test.stat_at_time('transactions', 1283195460), 12)
        self.assertEqual(self.test.stat_at_time('transactions', 1283195760), 1)
        self.assertEqual(self.test.stat_at_time('transactions', 1283195820), 11)

    def test_stat_at_time_page_requests(self):
        self.assertEqual(self.test.stat_at_time('Test time-page-requests', 1283195460), 2333)
        self.assertEqual(self.test.stat_at_time('Test time-page-requests', 1283195760), 2411)
        self.assertEqual(self.test.stat_at_time('Test time-page-requests', 1283195820), 2848)

    def test_stat_at_time_outside_range(self):
        self.assertEqual(self.test.stat_at_time('Test time', 9999999999), 0)
        self.assertEqual(self.test.stat_at_time('Errors', 9999999999), 0)

    def test_stat_at_time_unknown_stat(self):
        self.assertRaises(ValueError, self.test.stat_at_time, 'Fake Stat', 1283195460)

    def test_str(self):
        self.assertEqual(str(self.test), '1006: Sixth test')

    # TODO: Separate these into a TestGrinderBin class
    def test_bin_counts(self):
        self.assertEqual(self.test.bins[1283195460].count, 12)
        self.assertEqual(self.test.bins[1283195760].count, 1)
        self.assertEqual(self.test.bins[1283195820].count, 11)

    def test_bin_stats(self):
        self.assertEqual(
            self.test.bins[1283195460].stats,
            {
                '503 Errors': 0,
                'Errors': 0,
                'HTTP response code': 2400,
                'HTTP response length': 1956,
                'Test time': 28006,
            }
        )
        self.assertEqual(
            self.test.bins[1283195760].stats,
            {
                '503 Errors': 0,
                'Errors': 0,
                'HTTP response code': 200,
                'HTTP response length': 163,
                'Test time': 2411,
            }
        )
        self.assertEqual(
            self.test.bins[1283195820].stats,
            {
                '503 Errors': 0,
                'Errors': 0,
                'HTTP response code': 2200,
                'HTTP response length': 1793,
                'Test time': 31329,
            }
        )

    def test_bin_average(self):
        self.assertEqual(
            self.test.bins[1283195460].average('HTTP response length'), 163)


