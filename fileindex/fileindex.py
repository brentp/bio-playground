from tcdb.bdb import BDBSimple as BDB
import tcdb.bdb as tc
import sys
import gzip
import time


def nopen(f, mode="r"):
    """
    open a file that's gzipped or return stdin for '-'

    >>> nopen('-') == sys.stdin
    True
    >>> nopen(sys.argv[0])
    <open file '...', mode 'r' ...>
    """
    if not isinstance(f, basestring): return f
    return sys.stdin if f == "-" \
         else gzip.open(f, mode) if f.endswith(".gz") else open(f, mode)


class FileIndex(object):
    ext = ".fidx"

    @classmethod
    def _get_iterable(self, f):
        if isinstance(f, basestring):
            fh = nopen(f)
            name = fh.name
        else:
            fh = f
            name = getattr(f, 'name', "fileindex")
        return fh, name

    @classmethod
    def create(cls, file_like, get_next, allow_multiple=False):

        fh, name = cls._get_iterable(file_like)

        lines = sum(1 for line in fh)
        bnum = lines if lines > 2**24 else lines * 2
        fh.seek(0)
        db = BDB()
        db.open(name + cls.ext, bnum=bnum, lcnum=2**19,
                omode=tc.OWRITER | tc.OTRUNC | tc.OCREAT,
                apow=6, opts=tc.TLARGE, xmsiz=2**26)
        pos = fh.tell()
        putter = db.putcat if allow_multiple else db.put
        while True:
            key = get_next(fh)
            if not key: break
            # always append the | but only used by multiple.
            putter(key , str(pos) + "|")
            # fh has been moved forward by get_next.
            pos = fh.tell()
        fh.close()
        db.close()

    def __init__(self, file_like, call_class, allow_multiple=False):
        fh, name = self._get_iterable(file_like)
        self.filename = name
        self.allow_multiple = allow_multiple
        self.fh = fh
        self.call_class = call_class
        self.db = BDB()
        self.db.open(name + self.ext, omode=tc.OREADER)

    def __getitem__(self, key):
        # every key has the | appended.
        pos = self.db.get(key).rstrip("|")
        if self.allow_multiple:
            results = []
            for p in pos.split("|"):
                self.fh.seek(long(p))
                results.append(self.call_class(self.fh))
            return results

        self.fh.seek(long(pos))
        return self.call_class(self.fh)

    def __contains__(self, key):
        return key in self.db

if __name__ == "__main__":


    class FastQEntry(object):
        #__slots__ = ('name', 'seq', 'l3', 'qual', 'fpos')
        def __init__(self, fh):
            self.name = fh.readline().rstrip('\r\n')
            self.seq = fh.readline().rstrip('\r\n')
            self.l3 = fh.readline().rstrip('\r\n')
            self.qual = fh.readline().rstrip('\r\n')
        def __str__(self):
            return "\n".join((self.name, self.seq, self.l3, self.qual))


    def get_next(fh):
        name = fh.readline().strip()
        fh.readline(); fh.readline(); fh.readline()
        return name or None


    f = 'test.fastq'

    t = time.time()
    FileIndex.create(f, lambda fh: FastQEntry(fh).name)
    print "create:", time.time() - t

    fi = FileIndex(f, FastQEntry)
    entry = fi['@SRR040002.1_SL-XBC_0005_FC6124NAAXX:6:1:1091:4026/1']
    print entry

    import os; os.unlink(f + FileIndex.ext)
    del fi

    fh = open(f)

    FileIndex.create(fh, lambda fh: FastQEntry(fh).name)
    fi = FileIndex(open(f), FastQEntry)

    entry = fi['@SRR040002.1_SL-XBC_0005_FC6124NAAXX:6:1:1091:4026/1']
    print str(entry)
    os; os.unlink(f + FileIndex.ext)

    # test with gzipped file.
    gz = gzip.open('test.fastq.gz', 'w')
    gz.writelines(open(f))
    gz.close()
    gz = gzip.open('test.fastq.gz', 'r')

    FileIndex.create(gz, lambda fh: FastQEntry(fh).name)
    gz.close()
    gz = gzip.open('test.fastq.gz', 'r')
    fi = FileIndex(gz, FastQEntry)
    entry = fi['@SRR040002.1_SL-XBC_0005_FC6124NAAXX:6:1:1091:4026/1']
    print entry.name


    os.unlink(f + '.gz' + FileIndex.ext)
    os.unlink(f + '.gz')





