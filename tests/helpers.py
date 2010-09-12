# helpers.py

"""Helper functions and classes for unit tests.
"""

import tempfile

def write_test_data(filename, data):
    """Write ``filename`` containing the given ``data``.
    Leading space in each line is automatically stripped.
    """
    outfile = open(filename, 'w')
    for line in data.splitlines():
        outfile.write(line.lstrip() + '\n')
    outfile.close()


def write_tempfile(data):
    """Write a temporary file containing the given ``data`` string,
    and return the filename. Leading whitespace in each line is
    automatically stripped. Caller is responsible for deleting the
    temporary file after using it.
    """
    outfile = tempfile.NamedTemporaryFile(delete=False)
    for line in data.splitlines():
        outfile.write(line.lstrip() + '\n')
    outfile.close()
    return outfile.name

