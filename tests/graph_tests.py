#! /usr/bin/env python
# graph_tests.py

"""Unit tests for the csvsee.graph module
"""

import os, sys
# Append to sys.path in case csvsee isn't installed
sys.path.append(os.path.abspath('..'))

import doctest
import unittest

from csvsee import graph

class TestGraph (unittest.TestCase):
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
        top3 = graph.top_by_average(3, data.keys(), data)
        self.assertEqual(top3, ['a', 'b', 'c'])

        bottom3 = graph.top_by_average(3, data.keys(), data, drop=2)
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
            graph.top_by(sum, 3, data.keys(), data),
            ['a', 'b', 'c'])

        # Top 3 maximums
        self.assertEqual(
            graph.top_by(max, 3, data.keys(), data),
            ['e', 'd', 'c'])


if __name__ == '__main__':
    print("Running doctests...")
    doctest.testmod(graph)
    print("Running unit tests...")
    unittest.main()

