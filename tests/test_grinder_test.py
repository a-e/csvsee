import os
import csv
import unittest
from csvsee import grinder
from . import basic_dir

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
        test = grinder.Test(101, 'Foobared', 30)
        self.assertEqual(test.number, 101)
        self.assertEqual(test.name, 'Foobared')
        self.assertEqual(test.granularity, 30)


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


    def test_bin_counts(self):
        self.assertEqual(self.test.bins[1283195460].count, 12)
        self.assertEqual(self.test.bins[1283195760].count, 1)
        self.assertEqual(self.test.bins[1283195820].count, 11)


    def test_bin_average(self):
        self.assertEqual(
            self.test.bins[1283195460].average('HTTP response length'), 163)


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



