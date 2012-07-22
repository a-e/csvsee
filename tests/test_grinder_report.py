import os
import unittest
from csvsee import grinder
from . import basic_dir, data_dir, temp_filename

class TestGrinderReport (unittest.TestCase):
    def setUp(self):
        self.outfile = os.path.join(basic_dir, 'out_XP-0.log')
        self.data0 = os.path.join(basic_dir, 'data_XP-0.log')
        self.data1 = os.path.join(basic_dir, 'data_XP-1.log')


    def test_incomplete_outfile(self):
        """Test the `Report` class with an out* file having no test names
        (that is, a file that's either not a Grinder out* file, or one that
        hasn't finished writing test names to the end).
        """
        outfile = os.path.join(data_dir, 'incomplete', 'incomplete.log')
        self.assertRaises(grinder.NoTestNames, grinder.Report, 60, outfile)


    def test_granularity(self):
        report = grinder.Report(60, self.outfile, self.data0, self.data1)
        self.assertEqual(report.granularity, 60)

        report = grinder.Report(1, self.outfile, self.data0, self.data1)
        self.assertEqual(report.granularity, 1)


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


    def test_add(self):
        pass


    def test_add_unknown_test_number(self):
        pass


    def test_write_csv_test_time(self):
        report = grinder.Report(60, self.outfile, self.data0, self.data1)

        report_csv = temp_filename('csv')
        report.write_csv('Test time', report_csv)

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
        os.unlink(report_csv)


    def test_write_csv_transactions(self):
        report = grinder.Report(60, self.outfile, self.data0, self.data1)

        report_csv = temp_filename('csv')
        report.write_csv('transactions', report_csv)

        lines = [line.rstrip() for line in open(report_csv)]
        self.assertEqual(lines, [
            'GMT,1001: First test,1002: Second test,1003: Third test,1004: Fourth test,1005: Fifth test,1006: Sixth test',
            '08/30/2010 19:10:00.000,12,12,12,12,0,0',
            '08/30/2010 19:11:00.000,0,0,0,0,12,12',
            '08/30/2010 19:12:00.000,0,0,0,0,0,0',
            '08/30/2010 19:13:00.000,0,0,0,0,0,0',
            '08/30/2010 19:14:00.000,0,0,0,0,0,0',
            '08/30/2010 19:15:00.000,0,0,0,0,0,0',
            '08/30/2010 19:16:00.000,12,12,12,12,2,1',
            '08/30/2010 19:17:00.000,0,0,0,0,10,11',
        ])
        os.unlink(report_csv)


    def test_write_csv_page_requests(self):
        report = grinder.Report(60, self.outfile, self.data0, self.data1)

        report_csv = temp_filename('csv')
        report.write_csv('transactions-page-requests', report_csv)

        lines = [line.rstrip() for line in open(report_csv)]
        self.assertEqual(lines, [
            'GMT,1000: First page',
            '08/30/2010 19:10:00.000,13',
            '08/30/2010 19:11:00.000,0',
            '08/30/2010 19:12:00.000,0',
            '08/30/2010 19:13:00.000,0',
            '08/30/2010 19:14:00.000,0',
            '08/30/2010 19:15:00.000,0',
            '08/30/2010 19:16:00.000,12',
            '08/30/2010 19:17:00.000,0'
        ])
        os.unlink(report_csv)


    def test_write_all_csvs(self):
        report = grinder.Report(60, self.outfile, self.data0, self.data1)
        csv_prefix = temp_filename()
        report.write_all_csvs(csv_prefix)
        expect_csv_suffixes = [
            'Errors',
            'HTTP_response_code',
            'HTTP_response_length',
            'Test_time',
            'Test-time_page_requests_only',
            'Transaction_count',
            'Transaction_count_page_requests_only',
        ]
        expect_csv_files = [
            "%s_%s.csv" % (csv_prefix, suffix)
            for suffix in expect_csv_suffixes
        ]
        for filename in expect_csv_files:
            self.assertTrue(os.path.isfile(filename))

