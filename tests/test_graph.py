#! /usr/bin/env python
# test_graph.py

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


if __name__ == '__main__':
    print("Running doctests...")
    doctest.testmod(graph)
    print("Running unit tests...")
    unittest.main()

