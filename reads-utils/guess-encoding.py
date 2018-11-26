#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Guess the encoding of a stream of qual lines.

Accepts only quality scores as input, either on STDIN or
from a file provided as an argument.

Use cases: `awk 'NR % 4 == 0' <FASTQ> | %prog [options]`,
           `%prog [options] <quality scores file>`,
           `samtools view <BAM file> | cut -f 11 | %prog [options]`
"""

from __future__ import with_statement, division, print_function

import fileinput
import operator
import optparse
import sys

from collections import Counter

#  Note that the theoretical maximum for all encodings is 126.
#  The upper limits below are for "typical" data only.
RANGES = {
    'Sanger': (33, 73),
    'Illumina-1.8': (33, 74),
    'Solexa': (59, 104),
    'Illumina-1.3': (64, 104),
    'Illumina-1.5': (66, 105)
}

# The threshold to decide between Illumina-1.3 and Illumina-1.5
# based upon how common "B" is. The threshold insists it is
# within the Nth most common quality scores.
# N.B. needs to be conservative, as this is applied per input line.
N_MOST_COMMON_THRESH = 4


def get_qual_range(qual_str):
    """
    >>> get_qual_range("DLXYXXRXWYYTPMLUUQWTXTRSXSWMDMTRNDNSMJFJFFRMV")
    (68, 89...)
    """

    qual_val_counts = Counter(ord(qual_char) for qual_char in qual_str)

    min_base_qual = min(qual_val_counts.keys())
    max_base_qual = max(qual_val_counts.keys())

    return (min_base_qual, max_base_qual, qual_val_counts)


def get_encodings_in_range(rmin, rmax, ranges=RANGES):
    valid_encodings = []
    for encoding, (emin, emax) in ranges.items():
        if rmin >= emin and rmax <= emax:
            valid_encodings.append(encoding)
    return valid_encodings


def heuristic_filter(valid, qual_val_counts):
    """Apply heuristics to particular ASCII value scores
       to try to narrow-down the encoding, beyond min/max.
    """

    if 'Illumina-1.5' in valid:
        # 64–65: Phread+64 quality scores of 0–1 ('@'–'A')
        #        unused in Illumina 1.5+
        if qual_val_counts[64] > 0 or qual_val_counts[65] > 0:
            valid.remove('Illumina-1.5')

        # 66: Phread+64 quality score of 2 'B'
        #     used by Illumina 1.5+ as QC indicator
        elif 66 in map(operator.itemgetter(0),
                       qual_val_counts.most_common(N_MOST_COMMON_THRESH)):
            print("# A large number of 'B' quality scores (value 2, ASCII 66) "
                  "were detected, which makes it likely that this encoding is "
                  "Illumina-1.5, which has been returned as the only option.",
                  file=sys.stderr)
            valid = ['Illumina-1.5']

    return valid


def main():
    p = optparse.OptionParser(__doc__)
    p.add_option("-n", dest="n", help="number of qual lines to test default:-1"
                 " means test until end of file or until it it possible to "
                 " determine a single file-type",
                 type='int', default=-1)

    opts, args = p.parse_args()

    if len(args) > 1:
        print("Only a single input file is supported.", file=sys.stderr)
        sys.exit(1)

    gmin = 99
    gmax = 0
    valid = []

    err_exit = False

    input_file = fileinput.input(args, openhook=fileinput.hook_compressed)

    for i, line in enumerate(input_file):
        if i == 0:
            input_filename_for_disp = fileinput.filename()

            if fileinput.isstdin():
                input_filename_for_disp = 'STDIN'

            print("# reading qualities from "
                  "{}".format(input_filename_for_disp), file=sys.stderr)

        lmin, lmax, qual_val_counts = get_qual_range(line.rstrip())

        if lmin < gmin or lmax > gmax:
            gmin, gmax = min(lmin, gmin), max(lmax, gmax)
            valid = get_encodings_in_range(gmin, gmax)

            valid = heuristic_filter(valid, qual_val_counts)

            if len(valid) == 0:
                print("no encodings for range: "
                      "{}".format((gmin, gmax)), file=sys.stderr)
                err_exit = True
                break

            if len(valid) == 1 and opts.n == -1:
                # parsed entire file and found unique guess
                break

        if opts.n > 0 and i > opts.n:
            # parsed up to specified portion; return current guess(es)
            break

    input_file.close()

    if err_exit:
        sys.exit(1)
    else:
        print("{}\t{}\t{}".format(",".join(valid), gmin, gmax))


if __name__ == "__main__":
    import doctest
    if doctest.testmod(optionflags=doctest.ELLIPSIS |
                       doctest.NORMALIZE_WHITESPACE).failed == 0:
        main()
