# test_graph.py

"""Unit tests for the csvsee.graph module
"""

import os
import sys
import unittest
from csvsee import graph, utils
from . import csv_dir, temp_filename

class TestGraph (unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.png_file = temp_filename('png')
        cls.csv_file = os.path.join(csv_dir, 'response_time.csv')


    @classmethod
    def tearDownClass(cls):
        os.unlink(cls.png_file)


    def test_graph_default(self):
        """Test the `Graph` class with default settings.
        """
        g = graph.Graph(self.csv_file)
        g['title'] = 'Default settings'
        g.generate()
        g.save(self.png_file)
        self.assertTrue(os.path.isfile(self.png_file))
        # Show the graph, for a visual confirmation
        g.show()


    def test_graph_peak(self):
        """Test graphing of peak values.
        """
        g = graph.Graph(self.csv_file)
        g['peak'] = 3
        g['title'] = 'Peak values'
        g['ylabel'] = 'Response time'
        g['ymax'] = 2000
        g['truncate'] = 10
        g.generate()
        g.save(self.png_file)
        self.assertTrue(os.path.isfile(self.png_file))


    def test_graph_top(self):
        """Test graphing of top average values.
        """
        g = graph.Graph(self.csv_file)
        g['top'] = 3
        g['title'] = 'Top values'
        g['ylabel'] = 'Response time'
        g['ymax'] = 2000
        g['truncate'] = 10
        g.generate()
        g.save(self.png_file)
        self.assertTrue(os.path.isfile(self.png_file))


    def test_bad_extension(self):
        """Test saving to a filename with an unknown extension.
        """
        bad_ext = self.png_file + '.foo'
        g = graph.Graph(self.csv_file)
        self.assertRaises(ValueError, g.save, bad_ext)


    def test_bad_columns(self):
        """Test the use of bad column names.
        """
        g = graph.Graph(self.csv_file)
        g['x'] = 'Nonexistent column'
        self.assertRaises(utils.NoMatch, g.generate)

    def test_ylabel_prefix(self):
        """The ylabel = 'prefix' option uses the common column prefix
        as the y-axis label
        """
        g = graph.Graph(self.csv_file)
        g['ylabel'] = 'prefix'
        g.generate()
        self.assertEqual(g.axes.get_ylabel(), 'Request')

