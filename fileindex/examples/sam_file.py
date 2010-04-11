import sys
import os.path as op
sys.path.insert(0, op.join(op.dirname(__file__), ".."))
from fileindex import FileIndex

class SamLine(object):
    __slots__ = ('name', 'ref_loc', 'ref_seqid')
    def __init__(self, fh):
        line = fh.readline().split("\t") or [None]
        self.name = line[0]
        self.ref_seqid = line[2]
        self.ref_loc = int(line[3])
        # ... other sam format stuff omitted.

if __name__ == "__main__":
    f = '/usr/local/src/methylcode/emen/en-data/out/methylcoded.sam'
    if not op.exists(f + FileIndex.ext):
        FileIndex.create(f, lambda fh: SamLine(fh).name, allow_multiple=True)

    fi = FileIndex(f, SamLine, allow_multiple=True)
    print [(s.name, s.ref_seqid, s.ref_loc) for s in fi['23351265']]

