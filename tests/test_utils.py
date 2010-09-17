# test_utils.py

"""Unit tests for the `csvsee.utils` module
"""

import os
import csv
from datetime import datetime
from csvsee import utils
from . import write_tempfile


def test_grep():
    """Test grepping in text files.
    """
    # Sample log data
    filenames = [
        # Matching text on the same line as datestamp
        write_tempfile("""
            2010/08/30 13:57:14 Pushing up the daisies
            2010/08/30 13:58:08 Stunned
            2010/08/30 13:58:11 Stunned
            """),
        # Matching text on lines following datestamp
        write_tempfile("""
            2010/08/30 14:04:22
            Pining for the fjords
            2010/08/30 14:05:37
            Pushing up the daisies
            2010/08/30 14:09:48
            Pining for the fjords
            """),
    ]
    # Text to match
    matches = [
        'Pushing',
        'Pining',
        'Stunned',
    ]
    # Using 60-second resolution
    counts = utils.grep_files(filenames, matches, resolution=60)
    assert counts == [
        (datetime(2010, 8, 30, 13, 57), {'Pushing': 1, 'Pining': 0, 'Stunned': 0}),
        (datetime(2010, 8, 30, 13, 58), {'Pushing': 0, 'Pining': 0, 'Stunned': 2}),
        (datetime(2010, 8, 30, 14, 4), {'Pushing': 0, 'Pining': 1, 'Stunned': 0}),
        (datetime(2010, 8, 30, 14, 5), {'Pushing': 1, 'Pining': 0, 'Stunned': 0}),
        (datetime(2010, 8, 30, 14, 9), {'Pushing': 0, 'Pining': 1, 'Stunned': 0}),
    ]

    # Using 10-minute resolution
    counts = utils.grep_files(filenames, matches, resolution=600)
    assert counts == [
        (datetime(2010, 8, 30, 13, 50), {'Pushing': 1, 'Pining': 0, 'Stunned': 2}),
        (datetime(2010, 8, 30, 14, 0), {'Pushing': 1, 'Pining': 2, 'Stunned': 0}),
    ]
    for filename in filenames:
        os.unlink(filename)


def test_column_names():
    """Test the `utils.column_names` function.
    """
    filename = write_tempfile(
        """"Eastern Standard Time","Response Time","Response Length"
           "2010/05/19 13:45:50",419,2048
           "2010/05/19 13:45:55",315,2048
        """)
    assert utils.column_names(filename) == [
        'Eastern Standard Time', 'Response Time', 'Response Length']
    os.unlink(filename)



def test_top_by_avg():
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
    assert top3 == ['a', 'b', 'c']

    bottom3 = utils.top_by_average(3, data.keys(), data, drop=2)
    assert bottom3 == ['c', 'd', 'e']


def test_top_by_peak():
    """Test the `top_by_avg` function.
    """
    data = {
        'a': [2, 2, 2, 2, 8],
        'b': [1, 2, 2, 2, 7],
        'c': [1, 1, 2, 2, 6],
        'd': [1, 1, 1, 2, 5],
        'e': [1, 1, 1, 1, 4],
    }
    top3 = utils.top_by_peak(3, data.keys(), data)
    assert top3 == ['a', 'b', 'c']

    bottom3 = utils.top_by_peak(3, data.keys(), data, drop=2)
    assert bottom3 == ['c', 'd', 'e']


def test_top_by():
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
    assert utils.top_by(sum, 3, data.keys(), data) == ['a', 'b', 'c']

    # Top 3 maximums
    assert utils.top_by(max, 3, data.keys(), data) == ['e', 'd', 'c']


def test_xy_reader_with_timestamps():
    """Test the `read_xy_values` function with a ``.csv`` file containing
    timestamps.
    """
    filename = write_tempfile(
        """"Eastern Standard Time","Response Time","Response Length"
           "2010/05/19 13:45:50",419,2048
           "2010/05/19 13:45:55",315,2048
        """)

    # Test parsing with no gmt_offset or zero_time
    reader = csv.DictReader(open(filename))
    x_values, y_values = utils.read_xy_values(
        reader, 'Eastern Standard Time',
        ['Response Time', 'Response Length'],
        date_format='%Y/%m/%d %H:%M:%S')
    assert x_values == [
        datetime(2010, 5, 19, 13, 45, 50),
        datetime(2010, 5, 19, 13, 45, 55),
    ]
    assert y_values == {
        'Response Length': [2048.0, 2048.0],
        'Response Time': [419.0, 315.0],
    }

    # Test parsing with gmt_offset=6
    reader = csv.DictReader(open(filename))
    x_values, y_values = utils.read_xy_values(
        reader, 'Eastern Standard Time',
        ['Response Time', 'Response Length'],
        date_format='%Y/%m/%d %H:%M:%S',
        gmt_offset=6)
    assert x_values == [
        datetime(2010, 5, 19, 19, 45, 50),
        datetime(2010, 5, 19, 19, 45, 55),
    ]
    assert y_values == {
        'Response Length': [2048.0, 2048.0],
        'Response Time': [419.0, 315.0],
    }

    # Test parsing zero_time
    reader = csv.DictReader(open(filename))
    x_values, y_values = utils.read_xy_values(
        reader, 'Eastern Standard Time',
        ['Response Time', 'Response Length'],
        date_format='%Y/%m/%d %H:%M:%S',
        zero_time=True)
    assert x_values == [
        datetime(2010, 5, 19, 0, 0, 0),
        datetime(2010, 5, 19, 0, 0, 5),
    ]
    assert y_values == {
        'Response Length': [2048.0, 2048.0],
        'Response Time': [419.0, 315.0],
    }
    # Remove the temporary file
    os.unlink(filename)


def test_xy_reader_without_timestamps():
    """Test the `read_xy_values` function with a ``.csv`` file that
    does not contain timestamps, only numeric values.
    """
    filename = write_tempfile(
        """X,Y,Z
           0,2,3
           1,4,6
           2,6,9
           3,8,12
           4,10,15
        """)
    reader = csv.DictReader(open(filename))
    x_values, y_values = utils.read_xy_values(
        reader, 'X', ['Y', 'Z'])
    assert x_values == [0.0, 1.0, 2.0, 3.0, 4.0]
    assert y_values == {
        'Y': [2.0, 4.0, 6.0, 8.0, 10.0],
        'Z': [3.0, 6.0, 9.0, 12.0, 15.0],
    }
    # Remove the temporary file
    os.unlink(filename)

