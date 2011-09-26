#!/usr/bin/env python
r"""
BWA, BFAST and Mosaik, Bowtie and LifeScope all take colorspace reads in a
different format. There is no tool available to trim colorspace reads and
output a format that is compatible with all of those aligners.
This is an attempt to fill that gap.

Compatibility
=============
It can trim reads and output for
+ BWA (--prefix ends in .fq or .fastq and --encode is specified)
+ BFAST/Mosaik (--prefix ends in .fq/.fastq --encode is *NOT* specified)
+ Bowtie/LifeScope (--prefix does *NOT* end in .fq/.fastq and --encode is
*NOT* specified

Examples
========

This example will create the files example_ma_F3.csfasta and example_F3_QV.qual
trimming reads reads by creating a moving average of 7 bases and then keeping
all reads above 12 starting from the left end.
It will truncate reads with more than 3 '.'s
It will then discard any reads with a length less than 25.::

    $ %(prog)s -c $CSFASTA \
                 -q  $QUAL \
                 -p example_ma \
                 --max-ns 3 \
                 --moving-average 7:12 \
                 --min-read-length 25

if -p were example_ma.fastq, a .fastq file would be created for BFAST/Mosaik.
Adding --encode would make that compatible with BWA

if --min-read-length is not specified, all reads are kept, not matter how
short. This makes is simpler to post-process paired-end reads for joint
filtering.
"""
import argparse
import sys
import gzip
from itertools import izip
import string
import os

def nopen(f, mode="rb"):
    return {"r": sys.stdin, "w": sys.stdout}[mode[0]] if f == "-" \
         else gzip.open(f, mode) if f.endswith((".gz", ".Z", ".z")) \
        else open(f, mode)

def ma_setup(moving_average):
    moving_average = map(int, moving_average.split(":"))
    assert moving_average[0] % 2 != 0
    import numpy as np
    kern = np.ones(moving_average[0], dtype='f') / float(moving_average[0])

    def conv(cseq, quals, ma_min=moving_average[1]):
        ma_qual = np.convolve(quals, kern, mode="same")
        below = np.where(ma_qual < ma_min)[0]
        if len(below) == 0: return cseq, quals
        N = len(quals) - 1
        first_below = below[0]
        while first_below < N and ma_qual[first_below + 1] > ma_qual[below[0]]:
            first_below += 1
        if first_below < 2:
            return EMPTY
        return  cseq[:first_below], quals[:first_below]

    return conv

def gen_print_read(prefix, min_len):
    prefix, ext = os.path.splitext(prefix)


    # if the sent in prefix ends with .gz, we output gzip
    is_fastq = prefix.endswith((".fastq", ".fq")) or ext in (".fastq", ".fq") \
               or prefix == "-"
    if not ext.lower() in (".gz", ".z"):
        prefix += ext
        ext = ""

    prefix = prefix.rstrip('_')
    if is_fastq:
        out_fq = nopen(prefix + ext, "w")

        def print_read(header, cseq, quals):
            if header[0] == "#":
                #print >> out_fq, header,
                return
            if len(cseq) < min_len: return
            # Mosaik doesn't like it when seq longer than quals.
            if len(cseq) > len(quals):
                quals.append(min(quals[-3:]))
            print >>out_fq, "%s\n%s\n+\n%s" % (
                    "@" + header[1:].rstrip("\r\n").replace("_F3", "/1"),
                    cseq,
                    # between 33 and 64.
                    "".join("!" if q < 0 else "?" if q > 31 else chr(q + 33) for q in quals)
            )

    else:
        out_cs = nopen(prefix + "_F3.csfasta" + ext, "w")
        out_ql = nopen(prefix + "_F3_QV.qual" + ext, "w")

        def print_read(header, cseq, quals):
            if header[0] == "#":
                print >> out_cs, header,
                print >> out_ql, cseq,
                assert quals is None
                return
            if len(cseq) < min_len: return
            print >> out_cs, header,
            print >> out_cs, cseq
            print >> out_ql, header,
            print >> out_ql, " ".join(map(str, quals))

    return print_read, is_fastq

def qntrim(cs, quals, qn):
    """
    require N bases at or above Q otherwise filter
    """
    qlimit, nlimit = qn
    qq = sum(1 for q in quals if q >= qlimit)
    if qq < qlimit:
        return EMPTY
    return cs, quals

def main():
    p = argparse.ArgumentParser(description=__doc__,
                   formatter_class=argparse.RawDescriptionHelpFormatter)
    inputs = p.add_argument_group('inputs/outputs')
    inputs.add_argument("-c", dest="c", help="csfasta file", type=str)
    inputs.add_argument("-q", dest="q", help="qual file", type=str)


    inputs.add_argument("-p", "--prefix", dest="prefix", help="prefix of the output files"
            """ (does not include the '_F3'. if this endswith .fastq[.gz] .fq[.gz]
            the output is a single fastq file rather than new .csfasta, qual
            files. default is fastq to stdout.""", default="-")
    inputs.add_argument("--encode", action="store_true", default=False,
            help="output doubly encoded FASTQ sequences e.g. for use in BWA"
            "default is False, for use in Mosaik, BFAST")


    trimming = p.add_argument_group('trimming', 'options for trimming')
    trimming.add_argument("--min-qual", dest="minq", help="bases with quality"
            " below this value will be trimmed from the end",
            type=int, default=12)

    trimming.add_argument("--max-ns", dest="maxn", help="reads with"
            " more than this number of '.'s are chopped",
            type=int, default=12)

    trimming.add_argument("--moving-average", dest="ma", default=None, type=str,
            help="creating a moving average of window-size `window` on the "
            "quals chop as soon as the mov. avg. drops below `min` specified "
            " as: window:min e.g.: 7:12. The window must be odd")
    trimming.add_argument("--QN", dest="QN", help="chop reads with fewer"
        " than N bases with quality above Q. Specified as Q,N, e.g. 20,32 to"
        " require at least 32 bases >= phred 20 as in Ajay et. al GR paper")

    filtering = p.add_argument_group('filtering',
            'By default no filtering is done')
    filtering.add_argument("--min-read-length", dest="min_len", help="reads shorter"
            " than this after trimming are not printed. default: %(default)i",
             type=int , default=0)

    args = p.parse_args()
    if not (args.prefix and args.c and args.q):
        sys.exit(p.print_help())

    moving_average = args.ma
    if moving_average is not None:
        conv_fun = ma_setup(moving_average)

    qn = map(int, args.QN.split(",")) if args.QN else None

    print_read, is_fastq = gen_print_read(args.prefix, args.min_len)
    last_header = None
    stats = {'reads_chopped': 0, 'reads_total': 0, 'bases_skipped': 0}
    for cs, ql in izip(nopen(args.c), nopen(args.q)):
        if cs[0] in '#':
            assert ql[0] == cs[0]
            print_read(ql, cs, None)
        elif cs[0] == ">":
            stats['reads_total'] += 1
            assert ql == cs
            last_header = ql
        else:
            #don't skip, just truncate so paired-end can work with post-processing.
            if cs.count(".") > args.maxn:
                stats['reads_chopped'] += 1
                cs, quals = EMPTY

            else: # if it's already chopped, dont do this stuff.
                ql = ql.rstrip(" \r\n")
                cs = cs.rstrip(" \r\n")
                quals = map(int, ql.split(' '))

                len_cs = len(cs)
                assert len(quals) in (len_cs - 1, len_cs), (len(quals), len_cs)

                for i, q in enumerate(quals[::-1]):
                    if q > args.minq: break
                if i > 0:
                    quals = quals[:-i]
                    cs = cs[:-i]
                elif i == len(quals):
                    stats['reads_chopped'] += 1
                    cs, quals = EMPTY
                stats['bases_skipped'] += i

                if qn is not None:
                    cs, quals = qntrim(cs, quals, qn)

                if moving_average is not None and len(cs) > 1:
                    cs, quals = conv_fun(cs, quals)
            if not is_fastq:
                print_read(last_header, cs, quals)
            else:
                assert len(cs) != 0, (cs, quals, last_header, 1)
                if len(cs) > 2:
                    cs = double_encode(cs) if args.encode else cs
                    quals = quals[int(args.encode):]
                assert len(cs) != 0, (cs, quals, last_header, 2)
                print_read(last_header, cs, quals)

    for k in sorted(stats):
        print >>sys.stderr, "%-14s: %i" % (k, stats[k])

EMPTY = "..", [2]

def double_encode(cseq, _complement=string.maketrans('0123.', 'ACGTN')):
    # copied from BWA which takes substr(seq, 2, end)
    return cseq[2:].translate(_complement)

if __name__ == "__main__":
    import doctest
    if doctest.testmod(optionflags=doctest.ELLIPSIS |\
                                   doctest.NORMALIZE_WHITESPACE).failed == 0:
        main()
