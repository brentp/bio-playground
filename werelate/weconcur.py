"""
from we related, we get an iterable of query intervals where each query
interval has a list of related (overlapping) intervals from the other file(s).
given this list, e.g.:

    query1: [dba, dbb, dbc]
    query2: [dbc, dbd, dbe, dbf]

we can expand to:
    query1 dba
    query1 dbb
    query1 dbc
    query2 dbc
    query2 dbd
    query2 dbe
    query2 dbf

which are all the pairings. Then we can look at a particular column from query
and subject and see how often they co-occur. e.g.

    query1.sample_id, dba.sample_id ...
    query1.sample_id, dbb.sample_id ...

finally, we can repeatedly shuffle one of the columns and check the randomized
co-occurence without repeating the overlap test.
"""
import numpy as np
import collections
from werelate import relate, merge_files

def main():
    import argparse
    p = argparse.ArgumentParser("")
    p.add_argument("--a-col", type=int, help="1-based column in `afile` that indicates a grouping to test against file b")
    p.add_argument("--b-col", type=int, help="1-based column in `bfile` with grouping to test against file a")
    p.add_argument("--n-sims", type=int, help="number of simulations to run", default=20000)
    p.add_argument("afile", help="sorted bed file")
    p.add_argument("bfile", help="sorted bed file")
    a = p.parse_args()
    run(a)

def run(args):
    ai, bi = args.a_col - 1, args.b_col - 1

    avs, bvs = [], []
    for a in relate(merge_files(args.afile, args.bfile)):
        # TODO: add ops, e.g. below would be the default of all.
        # could also have max/min which convert to float and take max/min
        # and uniq which would use set(a.related).
        avs.extend([a.line[ai].rstrip("\r\n")] * len(a.related))
        bvs.extend(b.line[ai].rstrip("\r\n") for b in a.related)

    # convert to integers for faster shuffling and equality testing. 
    # TODO: handle floats with np.abs(avs - bvs) < delta.
    #       or handle floats with np.abs(avs - bvs).sum() or np.corrcoef(avs,
    #       bvs).
    ilookup = {p: i for i, p in enumerate(set(avs) | set(bvs))}
    avs = np.array([ilookup[a] for a in avs], dtype=np.int)
    bvs = np.array([ilookup[b] for b in bvs], dtype=np.int)

    obs = (avs == bvs).sum()

    exp = []
    for i in range(args.n_sims):
        np.random.shuffle(bvs)
        exp.append((avs == bvs).sum())

    ngt = sum(e >= obs for e in exp)
    print "p: %.3g (greater: %d)" % ((1.0 + ngt) / (1.0 + args.n_sims), ngt)


if __name__ == "__main__":
    main()
