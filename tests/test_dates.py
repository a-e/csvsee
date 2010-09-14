# test_dates.py

"""Unit tests for the `csvsee.dates` module
"""

import os
from datetime import datetime
from csvsee import dates
from nose.tools import assert_raises
from . import write_tempfile


def test_guess_date_format():
    """Test the `dates.guess_date_format` function.
    """
    date_formats = [
        ('2010/01/28 12:34:56 PM',      '%Y/%m/%d %I:%M:%S %p'),
        ('01/28/10 1:25:49 PM',         '%m/%d/%y %I:%M:%S %p'),
        ('01/28/2010 13:25:49.123',     '%m/%d/%Y %H:%M:%S.%f'),
        # Consider supporting alternative separators
        #('2010-01-28 12:34:56 PM', '%Y-%m-%d %I:%M:%S %p'),
    ]
    for date, format in date_formats:
        assert dates.guess_date_format(date) == format


def test_guess_file_date_format():
    """Test the `dates.guess_file_date_format` function.
    """
    # Sample file data, and expected format of that sample
    data_formats = [
        ('2010/01/28 12:34:56 PM',      '%Y/%m/%d %I:%M:%S %p'),
        ('01/28/10 1:25:49 PM',         '%m/%d/%y %I:%M:%S %p'),
        ('01/28/2010 13:25:49.123',     '%m/%d/%Y %H:%M:%S.%f'),
        ('2010/08/30 13:57:14 blah',    '%Y/%m/%d %H:%M:%S'),
        ('8/30/2010 13:57 blah',        '%m/%d/%Y %H:%M'),
        ('8/30/2010 1:57:00 PM blah',   '%m/%d/%Y %I:%M:%S %p'),
    ]
    # TODO: Move temp file creation into setUp
    for data, expected in data_formats:
        # Create a temporary file containing the data
        filename = write_tempfile(data)
        try:
            actual = dates.guess_file_date_format(filename)
        except:
            assert False
        else:
            assert actual == expected
        finally:
            # Remove the temp file
            os.unlink(filename)

    # TODO: Guess format in a .csv file


def test_guess_file_date_format_exception():
    filename = write_tempfile('Data file without a date')
    assert_raises(dates.CannotParseDate,
                  dates.guess_file_date_format,
                  filename)
    os.unlink(filename)


