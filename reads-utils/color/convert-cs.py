"""
convert colorspace reads with(out) quality to fastq(a). usage:
    %s reads.csfasta [reads_qv.qual] > some.fastq(a)

if .qual file is not specified, the output is fasta. otherwise, it is fastq.
quals are encoded like illumina-1.3+ reads with offset 64.
"""
import sys
from methylcoder import cs2seq
import os.path as op
from itertools import izip

__doc__ %= sys.argv[0]


def check_exists(path):
    if path is None: return
    if not op.exists(path):
        print >>sys.stderr, "%s does not exist" % path
        sys.exit(1)

def exhaust_comments(fh, doprint=False):
    if fh is None: return
    pos = fh.tell()
    while True:
        line = fh.readline()
        if line[0] != "#": break
        if doprint:
            print line,
        pos = fh.tell()
    fh.seek(pos)

def print_fastq(fc, fq):

    pairs = izip(fc, fq)
    while True:
        try:
            seq_header, qual_header = pairs.next()
        except StopIteration:
            break
        assert seq_header == qual_header, (seq_header, qual_header)
        assert seq_header[0] == ">"
        cs, qual = pairs.next()
        qual = qual.strip().split(" ")
        print "@%s" % seq_header[1:].strip()
        print cs2seq(cs.strip())
        print "+"
        print "".join(chr(int(q) + 33) for q in qual)

def print_fasta(fc):
    header = fc.readline()
    while header:
        print header,
        print cs2seq(fc.readline().strip())
        header = fc.readline()


def main(csfasta, quals=None):
    check_exists(csfasta)
    check_exists(quals)
    fc = open(csfasta)
    fq = open(quals) if quals else None

    exhaust_comments(fc, True)
    exhaust_comments(fq)

    if quals is None:
        print_fasta(fc)
    else:
        print_fastq(fc, fq)



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print >>sys.stderr, __doc__
        sys.exit()

    format = "fasta" if len(sys.argv) == 2 else "fastq"
    csfasta = sys.argv[1]
    quals = None if format == "fasta" else sys.argv[2]
    main(csfasta, quals)
