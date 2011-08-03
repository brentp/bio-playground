#!/bin/env python
"""
   partial sort of a file. Useful when some columns are known to be sorted, but
   within a group defined by those column, some other columns are out of order.
   e.g., if you have a bed file and you know it's already sorted by (or even
   just grouped by) chromosome, you can sort by start, stop within the
   chromosome without reading the entire bed-file into memory. The syntax for
   that would be::

       %(prog)s -g 0 -s 1n,2n my.bed > my.sorted.bed

    where the 'n' suffix indicates that it's a number. The default is to
    sort as a string.

"""
import argparse
from toolshed import reader, header as get_header
from itertools import groupby
from operator import itemgetter
import sys

def partsort(afile, group_cols, sort_cols, sort_convertors, header=False):
    """
    the converted columns are appended to the end of the row.
    then after the sort, these are removed.
    this removes problems with floating point reprs.
    """
    row_len = len(get_header(afile))
    n_extra = len(sort_convertors)

    # maintain order of the sort cols, but use the appended columns for the
    # numeric ones.
    actual_sort_cols = []
    n_extra = 0

    # since we append floats to the end *and* want to maintain the
    # requested sort order, we create the `actual_sort_cols`
    for c in sort_cols:
        if not c in sort_convertors:
            actual_sort_cols.append(c)
        else:
            idx = row_len + n_extra
            actual_sort_cols.append(idx)
            n_extra += 1

    # groupby the correct columns
    for keyed, group in groupby(reader(afile, header=header), lambda toks:
            [toks[i] for i in group_cols]):

        # then generate the rows with the converted columns appended.
        def gen_converted_group():
            for toks in group:
                # add the converted columns onto the end.
                yield toks + [fn(toks[col_idx]) for col_idx, fn in sort_convertors.items()]

        # then iterator over the sorted cols.
        for toks in sorted(gen_converted_group(), key=itemgetter(*actual_sort_cols)):
            # strip the extra columns.
            yield toks[:row_len]

def read_sort_spec(spec):
    toks = [x.strip() for x in spec.split(",")]
    col_idxs = map(int, (x.rstrip("n") for x in toks))
    col_convertors = dict([(i, float) for i, x in enumerate(toks) \
                                                  if x[-1] == "n"])
    return col_idxs, col_convertors


def main():
    p = argparse.ArgumentParser(description=__doc__,
                   formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-g", dest="g", help="these 0-based column numbers define a"
            " group and must already be sorted. Once these change, the group "
            " ends and is sorted by the columns defined in option `-s`")

    p.add_argument("-s", dest="s", help="these 0-based column numbers define"
            "the columns to sort on. if the column to be sorted is numeric "
            "(float or int) add a 'n'. e.g. -s 3n indicates that the 4th "
            "column should be converted to a number before sorting")

    p.add_argument('file', help='file to process', default="-")
    args = p.parse_args()
    if (args.g is None or args.s is None):
        sys.exit(not p.print_help())

    group_cols, group_convertors = read_sort_spec(args.g)
    sort_cols, sort_convertors = read_sort_spec(args.s)
    # group_convertors not used.

    for toks in partsort(args.file, group_cols, sort_cols, sort_convertors, header=False):
        print "\t".join(toks)

if __name__ == "__main__":
    import doctest
    if doctest.testmod(optionflags=doctest.ELLIPSIS |\
                                   doctest.NORMALIZE_WHITESPACE).failed == 0:
        main()
