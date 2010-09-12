#! /usr/bin/env python
# test_dates.py

"""Unit tests for the csvsee.dates module
"""

import os, sys
# Append to sys.path in case csvsee isn't installed
sys.path.append(os.path.abspath('..'))

import doctest
import unittest
import tempfile
import shutil
from datetime import datetime

from csvsee import dates
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


    def test_date_guessing(self):
        """Test the date-format-guessing functions.
        """
        # Guess format in a log file
        format = dates.guess_file_date_format(self.test_log)
        self.assertEqual(format, '%Y/%m/%d %H:%M:%S')

        # TODO: Guess format in a .csv file

        # Guess formats from a string
        date_formats = [
            ('2010/01/28 12:34:56 PM', '%Y/%m/%d %I:%M:%S %p'),
            ('01/28/10 1:25:49 PM', '%m/%d/%y %I:%M:%S %p'),
            ('01/28/2010 13:25:49.123', '%m/%d/%Y %H:%M:%S.%f'),
            # Consider supporting alternative separators
            #('2010-01-28 12:34:56 PM', '%Y-%m-%d %I:%M:%S %p'),
        ]
        for date, format in date_formats:
            self.assertEqual(dates.guess_date_format(date), format)


if __name__ == '__main__':
    print("Running doctests...")
    doctest.testmod(dates)
    print("Running unit tests...")
    unittest.main()

