# __init__.py

"""Setup and teardown methods for csvsee unit tests.
"""

import os
import tempfile

# Directory where test data files are stored
data_dir = os.path.join(os.path.dirname(__file__), 'data')
basic_dir = os.path.join(data_dir, 'basic')
csv_dir = os.path.join(data_dir, 'csv')
# Temporary directory for output files
temp_dir = tempfile.mkdtemp(prefix='csvsee_test')


# Helper functions

def write_tempfile(data):
    """Write a temporary file containing the given ``data`` string,
    and return the filename. Leading whitespace in each line is
    automatically stripped. Caller is responsible for deleting the
    temporary file after using it.
    """
    outfile = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False)
    for line in data.splitlines():
        outfile.write(line.lstrip() + '\n')
    outfile.close()
    return outfile.name


def temp_filename(ext=''):
    """Get a temporary filename with an optional extension.
    """
    temp = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False)
    temp.close()
    if ext:
        return temp.name + '.' + ext.lstrip('.')
    else:
        return temp.name

