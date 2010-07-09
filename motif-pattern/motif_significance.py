"""
calculate the Expect value of each pattern given a
file of occurences in the format

A B C [count]

where count is an integer number of occurrences
and A B C is the motif pattern.
"""
import collections
import random
import sys

def get_pattern_length_freqs(pattern_lengths):
    """
    >>> get_pattern_length_freqs({2: 12, 3: 0})
    {2: 1.0, 3: 0.0}

    >>> get_pattern_length_freqs({2: 12, 3: 12})
    {2: 1.0, 3: 0.5}

    >>> get_pattern_length_freqs({2: 12, 3: 12, 4: 24})
    {2: 1.0, 3: 0.75, 4: 0.5}

    """
    freqs = {}
    tot = float(sum(pattern_lengths.itervalues()))
    max_len = max(pattern_lengths.keys())
    pl = pattern_lengths.copy()
    pl[max_len + 1] = 0
    for n in sorted(pl, reverse=True):
        pl[n] += pl.get(n + 1, 0)

    freqs[max_len + 1] = 0
    for n in sorted(pattern_lengths, reverse=True):
        freqs[n] = pl[n] / tot
    del freqs[max_len + 1]
    #print freqs
    return freqs

def run_sim(pattern, motif_pool, length_freq, nsims):
    """
    return the number of times the pattern is created randomly.
    accounts for the length and the order
    """
    rand = random.random
    choice = random.choice
    seen = 0
    for _ in xrange(nsims):
        if rand() > length_freq: continue
        for l in pattern:
            if choice(motif_pool) != l: break
        else:
            seen += 1
    return seen

def read_motifs(fmotif):
    """
    create a random pool of motifs to choose from for the monte-carlo simulations
    """
    motif_pool = []
    for line in open(fmotif):
        if not line.strip(): continue
        if line[0] == "#": continue
        motif, count = line.rstrip().split()
        motif_pool.extend(motif * int(count))
    random.shuffle(motif_pool)
    return motif_pool

def read_patterns(fpatterns):
    patterns = []
    pattern_lengths = collections.defaultdict(int)
    for line in open(fpatterns):
        if not line.strip(): continue
        if line[0] == "#": continue
        line = line.strip().split()
        pattern, count = tuple(line[:-1]), int(line[-1])
        pattern_lengths[len(pattern)] += count
        patterns.append(pattern)

    pattern_length_freqs = get_pattern_length_freqs(pattern_lengths)
    return patterns, pattern_length_freqs


def main(fmotif, fpattern, nsims):
    motif_pool = read_motifs(fmotif)
    patterns, pattern_length_freqs = read_patterns(fpattern)

    for pattern in patterns:
        lfreq = pattern_length_freqs[len(pattern)]
        ngenerated = run_sim(pattern, motif_pool, lfreq, nsims)
        print " ".join(pattern), ngenerated / float(nsims)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    import optparse
    p = optparse.OptionParser(__doc__)
    p.add_option('-m', dest='motifs', help='path to file of motifs in format: "motif [count]" '
                 ' a single line would look like: "A 123"')
    p.add_option('-p', dest='patterns', help='path to file of patterns for which you to get the expect count')
    p.add_option('-n', dest='nsims', type='int', help='number of iterations for the simulation. higher is more accurate', default=10000)

    opts, _ = p.parse_args()
    if not (opts.motifs and opts.patterns):
        sys.exit(p.print_help())
    main(opts.motifs, opts.patterns, opts.nsims)
