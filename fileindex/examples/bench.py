import sys
import os
sys.path.insert(0, "/usr/local/src/screed")
sys.path.insert(0, "/usr/local/src/bio-playground/fileindex")
sys.path.insert(0, "/usr/local/src/biopython-sqlite/")
import screed
import fileindex
import bsddbfileindex
import time
import random

from Bio import SeqIO


def get_rand_headers(fq, N=100000):
    """ get N random headers from a fastq file without reading the
    whole thing into memory"""
    records = sum(1 for _ in open(fq)) / 4
    rand_records = sorted([random.randint(0, records) for _ in xrange(N)])
    
    headers = []
    fh = open(fq)
    rec_no = -1
    for rr in rand_records:
        while rec_no < rr:
            header = fh.readline().rstrip()
            for i in range(3): fh.readline()
            rec_no += 1
        headers.append(header)
    assert len(headers) == N, (len(headers),)
    random.shuffle(headers)
    return headers, records


class FastQEntry(object):
    __slots__ = ('name', 'seq', 'l3', 'qual', 'fpos')
    def __init__(self, fh):
        self.name = fh.readline().rstrip('\r\n')
        self.seq = fh.readline().rstrip('\r\n')
        self.l3 = fh.readline().rstrip('\r\n')
        self.qual = fh.readline().rstrip('\r\n')

def rm(f):
    try: os.unlink(f)
    except OSError: pass
    time.sleep(0.1)

def show_name(name):
    print "\n%s\n" % name + "-" * len(name)

def time_screed(f, random_seqs, name):
    show_name(name)
    rm("%s_%s" % (f, screed.dbConstants.fileExtension))

    t = time.time()
    screed.read_fastq_sequences(f)
    print "create: %.3f" % (time.time() - t)

    faqdb = screed.screedDB(f)
    t = time.time()
    for r in random_seqs:
        faqdb[r[1:]].sequence
    print "search: %.3f" % (time.time() - t)

def time_fileindex(f, random_seqs, name, klass):
    show_name(name)
    rm("%s%s" % (f, klass.ext))
    t = time.time()
    klass.create(f, lambda fh: FastQEntry(fh).name)
    print "create: %.3f" % (time.time() - t)

    fi = klass(f, FastQEntry)
    t = time.time()
    for r in random_seqs:
        fi[r].seq
    print "search: %.3f" % (time.time() - t)

def time_biopython_sqlite(f, random_seqs, name):
    show_name(name)
    idx = "%s.bidx" % f 
    rm(idx)
    t = time.time()
    fi = SeqIO.indexed_dict(f, idx, "fastq")
    print "create: %.3f" % (time.time() - t)

    t = time.time()
    for r in random_seqs:
        fi[r[1:]].seq
    print "search: %.3f" % (time.time() - t)



if __name__ == "__main__":

    f = "/usr/local/src/bowtie/bowtie-0.12.1/work/reads/s_1_sequence.txt"
    N = 100000

    rand_headers, nrecords = get_rand_headers(f, N)
    print "benchmarking fastq file with %i records (%i lines)" \
            % (nrecords, nrecords * 4)
    print "performing %i random queries" % len(rand_headers)


    time_screed(f, rand_headers, "screed")

    time_biopython_sqlite(f, rand_headers, "biopython-sqlite")

    time_fileindex(f, rand_headers, "fileindex", fileindex.FileIndex)

    time_fileindex(f, rand_headers, "bsddbfileindex", bsddbfileindex.FileIndex)
