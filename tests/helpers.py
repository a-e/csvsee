# helpers.py

"""Helper functions and classes for unit tests.
"""

def write_test_data(filename, data):
    """Write ``filename`` containing the given ``data``.
    Leading space in each line is automatically stripped.
    """
    outfile = open(filename, 'w')
    for line in data.splitlines():
        outfile.write(line.lstrip() + '\n')
    outfile.close()

