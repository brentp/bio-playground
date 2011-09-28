"""
Find peak-regions given a file of values (likely -log10(p)).
    %prog [options] data.file

e.g.

    %prog --skip 1000 --seed 5 --threshold 3 my.data.txt

will seed on values in the 2nd column that are larger than `5` and
extend as long as it continues to find values greater than `3` within `1000`
basepairs in either direction--where the locations is determined by the 1st
column.

if the -g options is used. The columns are:  "chromosome" "position" "value"
otherwise, they are: "position" "value".
The file must be be sorted by columns 1, 2 with `-g` and column 1 without `-g`

If --keep-cols is specified the final output column includes values from each
specified column *and* the value column (3rd column). for any rows above
the threshold.
"""

import argparse
from itertools import groupby
from operator import itemgetter
from toolshed import reader

def gen_regions(fh, skip, seed, threshold, group, keep_cols, report_cutoff):
    if group == False:
        def fhgen(): # insert None so that they all get grouped the same...
            for row in fh:
                row.insert(0, None)
                yield row
        fhiter = fhgen()
    else:
        fhiter = fh

    # turn the indexes into a function that returns their values.
    if keep_cols:
        # also keep the p-value...
        keep_cols.append(2)
        col_getter = itemgetter(*keep_cols)
    else:
        keep_cols = None
    for key, grouped in groupby(fhiter, itemgetter(0)):
        for region in find_region(grouped, skip, seed, threshold, col_getter,
                report_cutoff):
            yield key, region

def get_and_clear_region(region, col_getter, cutoff):
    start, end = region[0][0], region[-1][0]
    # r looks like: (67390903, ['chr10', '673903', '3.831', 'mm9-10-67390903'])
    rows = (r[1] for r in region if float(r[1][2]) > cutoff)

    extra = "|".join([",".join(col_getter(r)) for r in rows] if col_getter else [])
    l = len(region)
    region[:] = []
    return start, end, l, extra


def find_region(aiter, skip, seed, threshold, col_getter, report_cutoff):
    current_region = []
    seeded = False
    for row in aiter:
        chrom, pos, val = row[:3]
        pos = int(pos)
        val = float(val)
        # first check if we are too far away to continue the region.
        if seeded and pos - current_region[-1][0] > skip:
            yield get_and_clear_region(current_region, col_getter,
                    report_cutoff)
            assert current_region == []
            seeded = False
        elif current_region != [] and pos - current_region[-1][0] > skip:
            current_region = []
            assert seeded == False

        # if it's greater than the seed, everything's easy.
        if val >= seed:
            current_region.append((pos, row))
            seeded = True
        elif val >= threshold:
            current_region.append((pos, row))
        else:
            # nothing, it's not a large value
            pass

    if current_region and seeded:
        yield get_and_clear_region(current_region, col_getter, report_cutoff)



def main():
    p = argparse.ArgumentParser(__doc__)

    p.add_argument("-g", dest="group", help="group by the first column (usually"
                 " chromosome or probe) if this [optional]", default=False,
                 action="store_true")

    p.add_argument("--skip", dest="skip", help="Maximum number of intervening "
             "basepairs to skip before seeing a value. If this number is "
                 "exceeded, the region is ended chromosome or probe "
                 "[default: %default]", type=int, default=50000)
    p.add_argument("--min-region-size", dest="min-region", help="minimum "
            "length of the region. regions shorter than this are not printed"
                 "[default: %default] (no minimum)", type=int, default=0)
    p.add_argument("--seed", dest="seed", help="A value must be at least this"
                 " large in order to seed a region. [default: %default]",
                 type=float, default=5.0)
    p.add_argument("--keep-cols", dest="keep", help="comma separated list of"
            "columns to add to the output data")

    p.add_argument("--threshold", dest="threshold", help="After seeding, a value"
                 "of at least this number can extend a region [default: "
                 "%default]", type=float, default=3.0)
    p.add_argument("regions")

    args = p.parse_args()

    f = reader(args.regions, header=False, sep="\t")
    keep = map(int, args.keep.strip().split(","))
    report_cutoff = args.seed
    for key, region in gen_regions(f, args.skip, args.seed, args.threshold,
            args.group, keep, report_cutoff):
        print key + "\t" + "\t".join(map(str, region))


if __name__ == "__main__":
    import doctest
    if doctest.testmod(optionflags=doctest.ELLIPSIS).failed == 0:
        main()
