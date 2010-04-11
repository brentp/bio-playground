import sys
import os.path as op
sys.path.insert(0, op.join(op.dirname(__file__), ".."))
from fileindex import FileIndex

class FastQEntry(object):
    __slots__ = ('name', 'seq', 'l3', 'qual', 'fpos')
    def __init__(self, fh):
        self.name = fh.readline().rstrip('\r\n')
        self.seq = fh.readline().rstrip('\r\n')
        self.l3 = fh.readline().rstrip('\r\n')
        self.qual = fh.readline().rstrip('\r\n')

if __name__ == "__main__":
    f = '/usr/local/src/bowtie/bowtie-0.12.1/work/reads/s_1_sequence.txt'
    N = 100

    #if not op.exists(f + FileIndex.ext):
    FileIndex.create(f, lambda fh: FastQEntry(fh).name)

    fi = FileIndex(f, FastQEntry)
    print "getting %i keys..." % N

    for i, k in enumerate(fi.db.iterkeys(str)):
        print fi[k].seq
        if i == N: break


