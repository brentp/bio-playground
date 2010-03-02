"""
given a guess for ks, return a score (0 is perfect) for
the given sequence
"""
import random
import bisect

def score_guess(ks_guess, seqab, D, slen):
    substitutions = int(ks_guess * slen + 0.5)
    repeats = 1000
    outer_reps = 10

    diffs = []
    for rep in range(outer_reps):
        random.seed()
        ancestor = "".join([random.choice(seqab) for _ in range(slen)])
        for rep in xrange(repeats):
            amut = list(ancestor)
            bmut = list(ancestor)

            for i in xrange(substitutions):
                mut = random.choice((amut, bmut))
                mut[random.randint(0, slen - 1)] = random.choice(seqab)

            diff = sum([aa != bb for aa, bb in zip(amut, bmut)])
            diffs.append(diff)

    diffs.sort()

    idx0 = bisect.bisect_left(diffs, D - 10)
    idx1 = bisect.bisect_right(diffs, D + 10)
    n = (repeats * outer_reps) - abs(idx1 - idx0)
    return n


if __name__ == "__main__":
    l = "ACCACCAAAGCGCGCGCGGGG"
    score_guess(0.2, l, 12, len(l))
