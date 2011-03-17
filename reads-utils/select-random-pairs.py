"""
take paired end files and generate a new
set of paired end files with only a random
subset of reads. 

Usage:

    python %s reads_1.fastq reads_2.fastq 100

will take 100 random reads (still paired) from each file
and create the new files reads_1.fastq.subset and reads_2.fastq.subset
"""

import random
import sys

def write_random_records(fqa, fqb, N=100000):
    """ get N random headers from a fastq file without reading the
    whole thing into memory"""
    records = sum(1 for _ in open(fqa)) / 4
    rand_records = sorted([random.randint(0, records) for _ in xrange(N)])

    fha, fhb = open(fqa),  open(fqb)
    suba, subb = open(fqa + ".subset", "w"), open(fqb + ".subset", "w")
    rec_no = -1
    written = 0
    for rr in rand_records:
        while rec_no < rr:
            for i in range(4): fha.readline()
            for i in range(4): fhb.readline()
            rec_no += 1
        for i in range(4):
            suba.write(fha.readline())
            subb.write(fhb.readline())
        rec_no += 1
        written += 1
    assert written == N

    print >>sys.stderr, "wrote to %s, %s" % (suba.name, subb.name)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print __doc__ % sys.argv[0]
        sys.exit()

    N = 100 if len(sys.argv) < 4 else int(sys.argv[3])
    write_random_records(sys.argv[1], sys.argv[2], N)
