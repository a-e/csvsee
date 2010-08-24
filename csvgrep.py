#! /usr/bin/env python
# csvgrep.py

__doc__ = """Given one or more line-timestamped text files (such as log files),
count the number of matching phrases that occur each minute.

Usage::

    csvgrep.py -infiles <file1> <file2> -match <expr1> <expr2> -out <report.csv>
"""
usage = __doc__

import sys
from datetime import datetime
from csvsee import utils

def grep_files(infiles, matches):
    # Counts of each match, used as a template for each row
    row_temp = [(match, 0) for match in matches]
    rows = {}
    # Read each line of each infile
    for infile in infiles:
        for line in open(infile, 'r'):
            timestamp = utils.date_chop(line)

            # If this datestamp hasn't appeared before, add it
            if timestamp not in rows:
                rows[timestamp] = dict(row_temp)

            # Count the number of each match in this line
            for match in matches:
                if match in line:
                    rows[timestamp][match] += 1

    # Return a sorted list of (match, {counts}) tuples
    return sorted(rows.iteritems())


def grep_csv(infiles, matches, csvfile):
    outfile = open(csvfile, 'w')
    heading = '"Timestamp","%s"' % '","'.join(matches)
    outfile.write(heading + '\n')
    for (timestamp, counts) in grep_files(infiles, matches):
        line = '%s' % timestamp
        for match in matches:
            line += ',%s' % counts[match]
        outfile.write(line + '\n')
    outfile.close()


if __name__ == '__main__':
    if len(sys.argv) < 7:
        print(usage)
        sys.exit()
    else:
        args = sys.argv[1:]

    infiles = []
    matches = []
    csvfile = ''

    while len(args) > 0:
        opt = args.pop(0)
        if opt == '-infiles':
            while not args[0].startswith('-'):
                infiles.append(args.pop(0))
        elif opt == '-match':
            while not args[0].startswith('-'):
                matches.append(args.pop(0))
        elif opt == '-out':
            csvfile = args.pop(0)
        else:
            print(usage)
            print("Unknown option: '%s'" % opt)

    grep_csv(infiles, matches, csvfile)

