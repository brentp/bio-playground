#!/usr/bin/env python
"""
    find the probability that as high as `shared_genes` is random
    given the number of genes: `A_genes`, `B_genes` drawn from `total_genes`
    e.g.:

        $ %prog shared_genes total_genes A_genes B_genes

    or:

        $ %prog 10 30000 345 322
        0.0043679470685

    gives the probability that, 2 random gene subsets (chosen from 30000 genes)
    of length 345 and 322 would share at least 10 genes by chance.

    See: http://www.nslij-genetics.org/wli/pub/ieee-embs06.pdf

"""
import optparse
import sys
import scipy.stats as ss

def hypergeom(m, n, n1, n2, p=False):
    """
    >>> hypergeom(1, 1000, 1000, 1000) # has to be shared.
    1.0

    >>> all(hypergeom(i, 1000, 1000, 1000) == 1.0 for i in range(100))
    True

    >>> hypergeom(1, 30000, 20, 20)
    0.013253396616299651

    >>> hypergeom(2, 30000, 20, 20)
    7.9649366037104485e-05

    >>> hypergeom(11, 30000, 20, 20)
    4.516176321800458e-11

    >>> hypergeom(10, 30000, 20, 20) # very low prob.
    4.516176321800458e-11

    >>> hypergeom(20, 30000, 20, 20) # very low chance that all are shared.
    4.516176321800458e-11

    """
    if m <= 0: return 1.0
    mmin = m - 1
    mmax = min(n1, n2)
    return ss.hypergeom.cdf(mmax, n, n1, n2) - ss.hypergeom.cdf(mmin, n, n1, n2)


def main():
    p = optparse.OptionParser(__doc__)
    opts, args = p.parse_args()
    if (len(args) != 4):
        sys.exit(not p.print_help())
    args = map(long, args)
    m, n, n1, n2 = args
    print hypergeom(m, n, n1, n2)


if __name__ == "__main__":
    import doctest
    if doctest.testmod(optionflags=doctest.ELLIPSIS).failed == 0:
        main()

