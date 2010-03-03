import score_guess
print score_guess
from score_guess import score_guess
import scipy.optimize as so
import random
import numpy as np


a = """ATGTCGGGGCGCGGCAAGGGCGGCAAGGGGCTCGGCAAGGGCGGCGCGAAGAGGCATCGC
AAGGTGCTCCGCGACAACATCCAGGGCATCACCAAGCCGGCGATCCGGAGGCTGGCGAGG
AGGGGCGGCGTGAAGCGCATCTCCGGGCTGATCTACGAGGAGACCCGCGGCGTGCTCAAG
ATCTTCCTCGAGAACGTCATCCGCGACGCCGTCACCTACACGGAGCACGCCCGCCGCAAG
ACCGTCACCGCCATGGACGTCGTCTACGCGCTCAAGCGCCAGGGCCGCACCCTCTACGGC
TTCGGCGGCTGA"""
b = """ATGTCAGGTCGTGGAAAAGGAGGCAAGGGGCTCGGTAAGGGAGGAGCGAAGCGTCATCGG
AAAGTTCTCCGTGATAACATTCAGGGAATCACTAAGCCGGCTATCCGGCGTCTTGCGAGA
AGAGGTGGAGTGAAGAGAATCAGCGGGTTGATCTACGAGGAGACCAGAGGCGTTTTGAAG
ATCTTCTTGGAGAACGTTATTCGCGATGCTGTGACGTACACTGAGCACGCCAGGCGGAAG
ACGGTGACCGCCATGGATGTTGTTTACGCCCTTAAGAGGCAGGGAAGGACTCTGTACGGG
TTCGGTGGTTAA"""

aa = """ATGGCGGCGGCGGCGGCGGCGGCGGGGTACAGGGCGGAGGAGGAGTACGACTACCTGTTCAAGGTGGTGCTGATCGGGGACAGCGGCGTGGGGAAGTCGAACCTGCTGTCGCGGTTCGCGCGGGACGAGTTCAGCCTGGAGACCAGGTCCACCATCGGCGTCGAGTTCGCCACCAAGACCGTCCGCGTCGACGACAGGCTCGTCAAGGCCCAGATCTGGGACACCGCCGGCCAAGAGAGGTACCGCGCCATCACGAGCGCCTACTACCGCGGCGCGGTGGGCGCGCTGGTGGTGTACGACGTGACGCGCCGCATCACGTTCGAGAACGCGGAGCGGTGGCTCAAGGAGCTCCGCGACCACACGGACGCCAACATCGTCGTCATGCTCGTGGGCAACAAGGCCGACCTGCGCCACCTCCGCGCCGTCCCCGCGGAGGACGCCAGGGCGTTCGCCGAGGCGCACGGGACCTTCTCCATGGAGACGTCGGCGCTGGAGGCCACCAACGTGGAGGGCGCCTTCACCGAGGTGCTCGCGCAGATCTACCGCGTCGTCAGCCGGAACGCGCTCGACATCGGCGACGACCCCGCCGCGCCGCCCCGGGGGCGGACCATCGACGTCAGCGCCAAGGATGACGCCGTCACCCCCGTGAACAGCTCAGGGTGCTGCTCGTCTTGA"""
ab = """---------------ATGGCGTCGGGGTACCGCGCGGAGGAGGAGTACGACTACCTGTTCAAGGTGGTGCTGATCGGGGACAGCGGCGTGGGCAAGTCGAACCTGCTGTCGCGGTTCGCCAGGGACGAGTTCAGCCTCGAGACCAGGTCCACCATCGGCGTCGAGTTCGCCACCAAGACCGTCCAGGTCGACGACAAGCTCGTCAAGGCGCAGATCTGGGACACCGCCGGGCAGGAGAGGTACCGCGCCATCACGAGCGCATACTACCGCGGCGCGGTGGGCGCGCTGGTGGTGTACGACGTGACCCGCCGCATCACCTTCGACAACGCCGAGCGCTGGCTGCGGGAGCTGCGGGACCACACGGACGCCAACATCGTGGTCATGCTGGTGGGCAACAAGGCCGACCTGCGCCACCTCCGCGCCGTGACGCCCGAGGACGCCGCGGCCTTCGCGGAGCGGCACGGCACCTTCTCCATGGAGACGTCGGCGCTGGACGCCACCAACGTCGACCGCGCCTTCGCCGAGGTGCTCCGCCAGATCTACCACGTCGTCAGCCGGAACGCGCTCGACATCGGGGAGGACCCCGCCGCGCCGCCCAGGGGAAAGACCATCGACGTCGGCGCCGCCAAGGACGAGGTCTCCCCCGTGAATACGGGCGGCTGCTGCTCGGCTTAG"""

def clean_seqs(a, b): 
    # we only look at the 3rd basepair.
    seqa = a[2::3].upper()
    seqb = b[2::3].upper()

    ab = [sab for sab in zip(seqa, seqb) if not "-" in sab]
    seqa = "".join([s[0] for s in ab])
    seqb = "".join([s[1] for s in ab])
    return seqa, seqb

def calc_difference(a, b):
    return sum(aa != bb for aa, bb in zip(a, b))

def calc_acgt(a, b):
    s = a + b
    return s.count('A'), s.count('C'), s.count('G'), s.count('T')


def mleks(_seqa, _seqb):

    seqa, seqb = clean_seqs(_seqa, _seqb)
    D = calc_difference(seqa, seqb)

    seqab = seqa + seqb
    slen = len(seqab)/2

    scores = {}
    # give the optimizer the best guess from this range.
    for guess in (0.3, 0.5, 0.75, 1.1, 1.5):
        scores[guess] = score_guess(guess, seqab, D, slen)

    best_guess = sorted(scores.items(), key=lambda a: (a[1], a[0]))[0][0]
    def fnopt(ks_guess):
        return score_guess(ks_guess[0], seqab, D, slen)
    r = so.fmin(fnopt, best_guess, args=(), disp=False,
                xtol=0.1, maxfun=20)
    return r[0]


def gen_seqs(min_len=30, max_len=2000, min_gc=0.2, max_gc=0.8):
    print "l, a c g t, actual_difference, ks"
    for l in range(min_len, max_len, 50):
        for gc in np.arange(min_gc, max_gc, 0.1):
            L = 2 * l
            gs = int(L * gc) * "G"
            cs = int(L * gc) * "C" 
            was =int(L * (1 - gc)) * "A"
            ts = int(L * (1 - gc)) * "T" 
            choices = gs + cs + was + ts
            seq = "".join(random.choice(choices) for i in range(L))
            for rep in range(3):
                aseq = seq[:l]
                bseq = list(aseq[:])

                pos = random.randint(0, l - 1)
                bend = bseq[pos:]
                random.shuffle(bend)
                bseq = bseq[:pos] + bend
                bseq = "".join(bseq)

                aclean, bclean = clean_seqs(aseq, bseq)
                actual_acgt = calc_acgt(aclean, bclean)
                acgt = " ".join(map(str, actual_acgt))
                actual_difference = calc_difference(aclean, bclean)
                print l, acgt, actual_difference, mleks(aseq, bseq)

gen_seqs()





#print mleks(a.replace("\n", ""), b.replace("\n", ""))
