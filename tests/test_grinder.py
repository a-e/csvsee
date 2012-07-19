# test_grinder.py

"""Unit tests for the `csvsee.grinder` module.
"""

import os
import unittest
from csvsee import grinder
from . import basic_dir, data_dir

class TestGrinder (unittest.TestCase):
    def test_get_test_names(self):
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


    def test_grinder_files(self):
        # Expected out* and data* filenames
        outfile = os.path.join(basic_dir, 'out_XP-0.log')
        data0 = os.path.join(basic_dir, 'data_XP-0.log')
        data1 = os.path.join(basic_dir, 'data_XP-1.log')

        self.assertEqual(grinder.grinder_files(basic_dir), [
            (outfile, [data0, data1])
        ])

        # Exception on nonexistent directory
        self.assertRaises(ValueError, grinder.grinder_files, 'f00b4r')


