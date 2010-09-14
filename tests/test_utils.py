#! /usr/bin/env python
# test_utils.py

"""Unit tests for the csvsee.utils module
"""

import os, sys
# Append to sys.path in case csvsee isn't installed
sys.path.append(os.path.abspath('..'))

from datetime import datetime

from csvsee import utils
from helpers import write_tempfile


def test_grep():
    """Test grepping in text files.
    """
    # Sample log data
    filenames = [
        write_tempfile("""
            2010/08/30 13:57:14 Pushing up the daisies
            2010/08/30 13:58:08 Stunned
            2010/08/30 13:58:11 Stunned
            """),

        write_tempfile("""
            2010/08/30 14:04:22 Pining for the fjords
            2010/08/30 14:05:37 Pushing up the daisies
            2010/08/30 14:09:48 Pining for the fjords
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
    expected = [
        (datetime(2010, 8, 30, 13, 57), {'Pushing': 1, 'Pining': 0, 'Stunned': 0}),
        (datetime(2010, 8, 30, 13, 58), {'Pushing': 0, 'Pining': 0, 'Stunned': 2}),
        (datetime(2010, 8, 30, 14, 4), {'Pushing': 0, 'Pining': 1, 'Stunned': 0}),
        (datetime(2010, 8, 30, 14, 5), {'Pushing': 1, 'Pining': 0, 'Stunned': 0}),
        (datetime(2010, 8, 30, 14, 9), {'Pushing': 0, 'Pining': 1, 'Stunned': 0}),
    ]
    assert counts == expected

    # Using 10-minute resolution
    counts = utils.grep_files(filenames, matches, resolution=600)
    expected = [
        (datetime(2010, 8, 30, 13, 50), {'Pushing': 1, 'Pining': 0, 'Stunned': 2}),
        (datetime(2010, 8, 30, 14, 0), {'Pushing': 1, 'Pining': 2, 'Stunned': 0}),
    ]
    assert counts == expected


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

