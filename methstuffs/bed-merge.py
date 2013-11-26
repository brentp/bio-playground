"""
convert a number of separate, sorted files into a single file with 1 column per
file. merge only by the start value (assume length of intervals is 1).
useful for merging files from, e.g. bismark

python bed-merge.py --value-col 5 --name-re ".+/(\d+)." *.cov > out.matrix.txt
"""

import heapq
from itertools import groupby
import gzip
import os.path as op

xopen = lambda f: gzip.open(f) if f.endswith('.gz') else open(f)


class Row(object):
    __slots__ = ('chrom', 'start', 'end', 'value', 'source')

    def __init__(self, toks, val_col=4, source=None):
        self.chrom = toks[0]
        self.start, self.end = int(toks[1]), int(toks[2])
        self.value = toks[val_col - 1]
        self.source = source

    def __cmp__(self, other):
        return cmp(self.chrom, other.chrom) or cmp(self.start, other.start)


def bed_merge(row_iterables, sources):
    assert len(sources) == len(row_iterables)

    for loc, cgs in groupby(heapq.merge(*row_iterables),
                            lambda cg: (cg.chrom, cg.start)):

        cgs = list(cgs)
        cg = cgs[0]
        present = dict((c.source, c) for c in cgs)

        # if a file doesn't have a record for here, just append 0
        values = [(present[s].value if s in present else '0') for s in sources]
        yield cg.chrom, cg.start, cg.end, values


def gen_iterable(fname, val_col):
    source = source_from_fname(fname)
    for toks in (x.rstrip("\r\n").split("\t") for x in xopen(fname)):
        yield Row(toks, val_col, source)


if __name__ == "__main__":

    import argparse
    import re
    p = argparse.ArgumentParser(__doc__)
    p.add_argument("--value-col", type=int, default=4)
    p.add_argument("--name-re", default=r"/?(.+)$",
            help="regexp to convert file name to sample name")
    p.add_argument("bed_files", nargs="+", help="sorted bed files")

    a = p.parse_args()
    name_re = re.compile(r"%s" % a.name_re)

    def source_from_fname(fname):
        try:
            return name_re.match(fname).groups(0)[0]
        except:
            return op.basename(fname)

    iterables = [gen_iterable(f, a.value_col) for f in a.bed_files]
    sources = [source_from_fname(f) for f in a.bed_files]


    fmt = "{chrom}:{start}\t{vals}"
    print "probe\t%s" % "\t".join(sources)
    for chrom, start, end, values in bed_merge(iterables, sources):
        if sum(float(v) for v in values) < 24: continue
        if sum(float(v) > 0 for v in values) < 2: continue
        vals = "\t".join(values)
        print fmt.format(chrom=chrom, start=start, vals=vals)

