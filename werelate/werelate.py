"""Streaming relation (overlap, distance) testing of (any number of) sorted files of intervals."""
from __future__ import print_function

import sys
import gzip
import heapq
import itertools as it
from operator import attrgetter
from collections import namedtuple
try:
    filter = it.ifilter
except AttributeError: # python3
    pass

########################################################################
########################################################################
# this section is mostly uninteresting code to:
# 1. "parse" the intervals
# 2. sort them into a single iterable across files (using heapq.merge in python).
# 3. group them by chrom (using itertools.groupby)
# this is all done lazily streaming over the intervals.
########################################################################
########################################################################

def xopen(f):
    return gzip.open(f) if f.endswith('.gz') \
                        else sys.stdin if f == "-" \
                        else open(f)

# related will be a list of all things that are related to the given interval
Interval = namedtuple('Interval', 'chrom start end fh line related i'.split())

class BedIter(object):
    __slots__ = "fh chrom start end header i line_num".split()
    def __init__(self, fname, i=None, chrom=0, start=1, end=2):
        self.fh = xopen(fname)
        self.chrom, self.start, self.end = chrom, start, end
        self.header = None
        self.i = i
        self.line_num = 0

    def __iter__(self):
        return self

    def next(self):
        line = next(self.fh).split("\t")
        self.line_num += 1
        if self.line_num == 1:
            try:
                chrom, start = line[self.chrom], int(line[self.start])
            except:
                line = next(self.fh).split("\t")
                self.line_num += 1
                chrom, start = line[self.chrom], int(line[self.start])
        else:
            chrom, start = line[self.chrom], int(line[self.start])

        # yield chrom and start so that heapq.merge works
        return Interval(chrom, start, int(line[self.end]), self.fh, line, [], self.i)
    __next__ = next

def merge_files(*beds):
    beds = [BedIter(f, i=i) for i, f in enumerate(beds)]
    return merge_beds(beds)

def merge_beds(beds):
    for item in heapq.merge(*beds):
        yield item

def relate(merged):
    iterable = it.groupby(merged, attrgetter('chrom'))

    seenChroms, lastChrom = set(), None

    for chrom, li in iterable:
        if chrom in seenChroms and chrom != lastChrom:
            raise Exception("chromosomes wout of order between files: %s, %s" %
                            (chrom, lastChrom))
        lastChrom = chrom
        seenChroms.add(chrom)
        # we know everything in li is from the same chrom
        start = -1
        for interval in werelate(li):
            if interval.start < start:
                raise Exception("intervals out of order: %s after %d" % (interval, start))
            start = interval.start
            yield interval

############################################################################
############################################################################
# The section below is more interesting with the `werelate` function taking
# an iterable of intervals and simply sending the appropriate intervals to
# `check_related`. Each time `check_related` returns
# True, info about the related interval is added to the other so the relations


# example function to check for overlap or check within distance
def check_related_distance(a, b, distance=0):
    # note with distance == 0 this just overlap.
    assert a.start <= b.start and a.chrom == b.chrom
    return b.start - distance < a.end

def werelate(interval_iter, check_related=check_related_distance):
    """
    Flexible overlap, or proximity testing and reporting.

    Arguments
    ---------

    interval_iter: iterable
        a lazy iterable of Intervals sorted by start position and from the same
        chromosome.

    check_related: function(a Interval, b Interval) -> bool
        a function that accepts 2 intervals and tells if they are related.
        Since the input is assumed to be sorted, it is assumed that if the
        function returns false, the a Interval can not possibly be related to
        any interval after the b Interval and so it can be yielded (and not
        tested against any remaining intervals in the stream).
        See check_related_distance and for example.
    """
    cache = [next(interval_iter)]
    for interval in interval_iter:
        for i, c in enumerate(cache):
            if check_related(c, interval):
                # they must overlap. add each to the other's related pile
                if c.fh != interval.fh:
                    if c.i == 0:
                        c.related.append(interval)
                    elif interval.i == 0:
                        interval.related.append(c)
            else:
                # only report intervals from the query.
                if c.i == 0:
                    yield c
                cache[i] = None

        cache = list(filter(None, cache)) + [interval]

    for c in filter(None, cache):
        if c.i == 0:
            yield c

if __name__ == "__main__":
    import sys
    for b in relate(merge_files(*sys.argv[1:])):
        print("\t".join(map(str, (b.chrom, b.start, b.end,
                                  "\t".join(b.line[3:]).rstrip("\n"), len(b.related)))))
