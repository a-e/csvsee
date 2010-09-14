# __init__.py

"""Setup and teardown methods for csvsee unit tests.
"""

import os
import sys
import tempfile
import shutil

# Directory where test data files are stored
data_dir = os.path.join(os.path.dirname(__file__), 'data')
# Temporary directory for output files
temp_dir = tempfile.mkdtemp(prefix='csvsee_test')


# Package-level setup and teardown

def setup():
    """Package-level setup.
    """
    # Append to sys.path in case csvsee isn't installed
    sys.path.append(os.path.abspath('..'))


def teardown():
    """Package-level teardown.
    """
    # Remove temporary output folder
    shutil.rmtree(temp_dir)


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

