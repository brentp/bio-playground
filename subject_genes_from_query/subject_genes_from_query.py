"""
no annotations for the subject, so the blast(z) is just query features against
subject genomic sequence.
we use the subject hits as the new features by:
    + overlapping subject hits are merged into single hsps
    + nearby subject hits to the same query are merge into single HSPs
    + no introns are recorded.

bed and feature fasta files are created.
"""
import sys
import collections
from pyfasta import Fasta
import numpy as np
import os.path as op
from itertools import tee, izip

blast_file = sys.argv[1]
subject_fasta_file = sys.argv[2]

out_fasta = "%s.features%s" % op.splitext(subject_fasta_file)

by_subject = collections.defaultdict(list)
fa = Fasta(subject_fasta_file)

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

by_subject = {}
seqids = []
for seqid in fa.iterkeys():
    by_subject[seqid] = np.zeros((len(fa[seqid]) + 1,), dtype=np.uint8)
    seqids.append((len(fa[seqid]),seqid))


by_query_subject = collections.defaultdict(dict)
for line in open(blast_file):
    args = line.split("\t")
    query, subject = args[0], args[1]
    sstart, sstop = sorted(map(int, args[8:10]))
    by_subject[subject][sstart: sstop + 1] |= 1
    if not subject in by_query_subject[query]:
        by_query_subject[query][subject] = [(sstart, sstop)]
    else:
        by_query_subject[query][subject].append((sstart, sstop))

# if 2 HSPs are nearby on the subject and from the same query, merge them into a single HSP
NEAR_SAME = 1000
for query in by_query_subject:
    for subject in by_query_subject[query]:
        li = sorted(by_query_subject[query][subject])
        if len(li) < 2: continue
        for alocs, blocs in pairwise(li):

            if blocs[0] - alocs[1] < NEAR_SAME:
                by_subject[subject][alocs[1]: blocs[0] + 1] |= 1



print >>sys.stderr, "writing features.fasta to: %s" % out_fasta
out = open(out_fasta, "w")

for seqlen, seqid in sorted(seqids, reverse=True):
    masks = by_subject[seqid]
    starts, = np.where((masks[:-1] == 0) & (masks[1:] == 1))
    ends,   = np.where((masks[:-1] == 1) & (masks[1:] == 0))

    for s, e in zip(starts, ends):
        assert s < e, (s, e, seqid)
        # add 1 for 0-based and 1 for the [1:]
        start = s + 2
        end = e + 1
        name = "%s-%i-%i" % (seqid, start, end)
        print "%s\t%i\t%i\t%s" % (seqid, s + 1, e, name)
        print >>out, ">" + name
        print >>out, fa[seqid][start - 1: end]
