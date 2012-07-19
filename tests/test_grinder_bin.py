import unittest
from csvsee import grinder

class TestGrinderBin (unittest.TestCase):
    def test_init(self):
        stat_dict = {'Errors': 0, 'HTTP response length': 0, 'Test time': 0}
        stat_names = stat_dict.keys()
        bin = grinder.Bin(stat_names)
        self.assertEqual(bin.stats, stat_dict)
        self.assertEqual(bin.count, 0)

    def test_add(self):
        stat_names = ['Errors', 'Muffins']
        bin = grinder.Bin(stat_names)
        bin.add({'Errors': 1, 'Muffins': 2})
        self.assertEqual(bin.count, 1)
        self.assertEqual(bin.stats, {'Errors': 1, 'Muffins': 2})
        bin.add({'Errors': 0, 'Muffins': 3})
        self.assertEqual(bin.count, 2)
        self.assertEqual(bin.stats, {'Errors': 1, 'Muffins': 5})
        bin.add({'Errors': 2, 'Muffins': 1})
        self.assertEqual(bin.count, 3)
        self.assertEqual(bin.stats, {'Errors': 3, 'Muffins': 6})
        bin.add({'Errors': 0, 'Muffins': 0})
        self.assertEqual(bin.count, 4)
        self.assertEqual(bin.stats, {'Errors': 3, 'Muffins': 6})

    def test_average(self):
        stat_names = ['Errors', 'Muffins']
        bin = grinder.Bin(stat_names)
        self.assertEqual(bin.average('Errors'), 0)
        self.assertEqual(bin.average('Muffins'), 0)
        bin.add({'Errors': 1, 'Muffins': 2})
        bin.add({'Errors': 2, 'Muffins': 4})
        bin.add({'Errors': 1, 'Muffins': 6})
        self.assertEqual(bin.average('Errors'), 1)
        self.assertEqual(bin.average('Muffins'), 4)


