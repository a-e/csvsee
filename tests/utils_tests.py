#! /usr/bin/env python
# utils_tests.py

"""Unit tests for the csvsee.utils module
"""

import os, sys
# Append to sys.path in case csvsee isn't installed
sys.path.append(os.path.abspath('..'))

import doctest
import unittest
import tempfile
import shutil
from datetime import datetime

from csvsee import utils
from helpers import write_test_data


class TestLogs (unittest.TestCase):
    # Sample log data
    logdata = """
        2010/08/30 13:57:14 Pushing up the daisies
        2010/08/30 13:58:08 Stunned
        2010/08/30 13:58:11 Stunned
        2010/08/30 14:04:22 Pining for the fjords
        2010/08/30 14:05:37 Pushing up the daisies
        2010/08/30 14:09:48 Pining for the fjords
        """

    def setUp(self):
        """Create .log files to test on.
        """
        # Temporary directory to hold test data
        self.tempdir = tempfile.mkdtemp(prefix='csvsee')
        # Test .log filenames
        self.test_log = os.path.join(self.tempdir, 'test.log')
        # Write test data
        write_test_data(self.test_log, self.logdata)


    def tearDown(self):
        """Remove test data directory.
        """
        shutil.rmtree(self.tempdir)


    def test_grep(self):
        """Test grepping in text files.
        """
        filenames = [self.test_log]
        matches = [
            'Pushing',
            'Pining',
            'Stunned',
        ]
        # Using 60-second resolution
        counts = utils.grep_files(filenames, matches, resolution=60)
        expected = [
            (datetime(2010, 8, 30, 13, 57), {'Pushing': 1, 'Pining': 0, 'Stunned': 0}),
            (datetime(2010, 8, 30, 13, 58), {'Pushing': 0, 'Pining': 0, 'Stunned': 2}),
            (datetime(2010, 8, 30, 14, 4), {'Pushing': 0, 'Pining': 1, 'Stunned': 0}),
            (datetime(2010, 8, 30, 14, 5), {'Pushing': 1, 'Pining': 0, 'Stunned': 0}),
            (datetime(2010, 8, 30, 14, 9), {'Pushing': 0, 'Pining': 1, 'Stunned': 0}),
        ]
        self.assertEqual(counts, expected)

        # Using 10-minute resolution
        counts = utils.grep_files(filenames, matches, resolution=600)
        expected = [
            (datetime(2010, 8, 30, 13, 50), {'Pushing': 1, 'Pining': 0, 'Stunned': 2}),
            (datetime(2010, 8, 30, 14, 0), {'Pushing': 1, 'Pining': 2, 'Stunned': 0}),
        ]
        self.assertEqual(counts, expected)


class TestCsv (unittest.TestCase):
    # Sample csv data
    csvdata = """
        Timestamp,
        """

    def setUp(self):
        """Create .csv files to test on.
        """
        # Temporary directory to hold test data
        self.tempdir = tempfile.mkdtemp(prefix='csvsee')
        # Test .csv filenames
        self.test_csv = os.path.join(self.tempdir, 'test.csv')
        # Write test data
        write_test_data(self.test_csv, self.csvdata)

        #reader = csv.DictReader(open(self.csv_file, 'r'))


    def tearDown(self):
        """Remove test data directory.
        """
        shutil.rmtree(self.tempdir)


class TestTop (unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_top_by_avg(self):
        """Test the `top_by_avg` function.
        """
        data = {
            'a': [2, 2, 2, 2, 2],
            'b': [1, 2, 2, 2, 2],
            'c': [1, 1, 2, 2, 2],
            'd': [1, 1, 1, 2, 2],
            'e': [1, 1, 1, 1, 2],
        }
        top3 = utils.top_by_average(3, data.keys(), data)
        self.assertEqual(top3, ['a', 'b', 'c'])

        bottom3 = utils.top_by_average(3, data.keys(), data, drop=2)
        self.assertEqual(bottom3, ['c', 'd', 'e'])


    def test_top_by(self):
        """Test the `top_by` function.
        """
        data = {
            'a': [5, 5, 5],
            'b': [4, 4, 6],
            'c': [3, 3, 7],
            'd': [2, 2, 8],
            'e': [1, 1, 9],
        }
        # Top 3 sums
        self.assertEqual(
            utils.top_by(sum, 3, data.keys(), data),
            ['a', 'b', 'c'])

        # Top 3 maximums
        self.assertEqual(
            utils.top_by(max, 3, data.keys(), data),
            ['e', 'd', 'c'])


if __name__ == '__main__':
    print("Running doctests...")
    doctest.testmod(utils)
    print("Running unit tests...")
    unittest.main()

