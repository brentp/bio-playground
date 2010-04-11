from tcdb.bdb import BDB
import tcdb.bdb as tc

class FileIndex(object):
    ext = ".fidx"
    @classmethod
    def create(cls, filename, get_next, allow_multiple=False):
        fh = open(filename)
        lines = sum(1 for line in fh)
        bnum = lines if lines > 2**24 else lines * 2
        fh.seek(0)
        db = BDB()
        db.open(filename + cls.ext, bnum=bnum, lcnum=2**19,
                omode=tc.OWRITER | tc.OTRUNC | tc.OCREAT,
                apow=6, opts=tc.TLARGE, xmsiz=2**26)        
        pos = fh.tell()
        putter = db.putcat if allow_multiple else db.put
        while True:
            key = get_next(fh)
            if not key: break
            # always append the | but only used by multiple.
            putter(key , str(pos) + "|", True, True)
            # fh has been moved forward by get_next.
            pos = fh.tell()
        fh.close()
        db.close()

    def __init__(self, filename, call_class, allow_multiple=False):
        self.filename = filename
        self.allow_multiple = allow_multiple
        self.fh = open(self.filename)
        self.call_class = call_class
        self.db = BDB()
        self.db.open(filename + self.ext, omode=tc.OREADER)

    def __getitem__(self, key):
        # every key has the | appended.
        pos = self.db.get(key, None, True, str).rstrip("|")
        if self.allow_multiple:
            results = []
            for p in pos.split("|"):
                self.fh.seek(long(p))
                results.append(self.call_class(self.fh))
            return results
                
        self.fh.seek(long(pos))
        return self.call_class(self.fh)

if __name__ == "__main__":
    import time
    class FastQEntry(object):
        __slots__ = ('name', 'seq', 'l3', 'qual', 'fpos')
        def __init__(self, fh):
            self.name = fh.readline().rstrip('\r\n')
            self.seq = fh.readline().rstrip('\r\n')
            self.l3 = fh.readline().rstrip('\r\n')
            self.qual = fh.readline().rstrip('\r\n')
 
    def get_next(fh):
        name = fh.readline().strip()
        fh.readline(); fh.readline(); fh.readline()
        return name or None
    #f = '/usr/local/src/methylcode/500K.fastq'
    f = '/usr/local/src/bowtie/bowtie-0.12.1/work/reads/s_1_sequence.txt'

    t = time.time()
    #FileIndex.create(f, lambda fh: FastQEntry(fh).name)
    print time.time() - t

    fi = FileIndex(f, FastQEntry)
    N = 1000000 
    NKeys = N
    print "getting %i keys..." % N

    it = fi.db.iterkeys(str)
    keys = [it.next() for i in xrange(N)]
    import random
    print "shuffling"
    random.shuffle(keys)
    keys = keys[:N]
    print "timing" 
    t = time.time()
    for k in keys:
        entry = fi[k].name
    print time.time() - t
    print len(keys) / (time.time() - t) , "queries per second"
