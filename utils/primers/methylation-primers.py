"""
batch Methylation primer design using the `MethPrimer`_ site

http://www.urogene.org/methprimer/index1.html
"""

post_data = """\
SEQUENCE:%(seq)s
PRIMER_TASK:PICK_PCR_PRIMERS
CPG_ISLAND_SIZE:100
CPG_SHIFT:1
CPG_OE:0.6
CPG_ISLAND_PERCENT:50.0
Pick Primers:Submit
PRIMER_SEQUENCE_ID:
TARGET:
EXCLUDED_REGION:
PRIMER_NUM_RETURN:9
PRODUCT_MIN_SIZE:%(prod_min)i
PRIMER_PRODUCT_OPT_SIZE:%(prod_opt)i
PRODUCT_MAX_SIZE:%(prod_max)i
PRIMER_MIN_TM:%(tmin)i
PRIMER_OPT_TM:%(topt)i
PRIMER_MAX_TM:%(tmax)i
PRIMER_MIN_SIZE:%(pmin)i
PRIMER_OPT_SIZE:%(popt)i
PRIMER_MAX_SIZE:%(pmax)i
PROD_CG_MIN:4
PRIMER_MAX_POLY_X:5
NUM_CS:4
PRIMER_MAX_POLY_T:8
CG_3_POSITION:3
NUM_CGS:1
SET_TA_DIFF:5"""

import re
from itertools import groupby
from toolshed import nopen

SPACES = re.compile(r"\s{2,}")
COLUMNS = "Primer            Start Size  Tm      GC%   'C's Sequence".split()
COLUMNS = ["sequence", COLUMNS[0]] + ["left-" + c for c in COLUMNS[1:]] \
                                   + ["right-" + c for c in COLUMNS[1:]]


def fasta_iter(fasta_name):
    """
    given a fasta file. yield tuples of header, sequence
    """
    fh = nopen(fasta_name)
    # ditch the boolean (x[0]) and just keep the header or sequence since
    # we know they alternate.
    faiter = (x[1] for x in groupby(fh, lambda line: line[0] == ">"))
    for header in faiter:
        # drop the ">"
        header = header.next()[1:].strip()
        # join all sequence lines to one.
        seq = "".join(s.strip() for s in faiter.next())
        yield header, seq

def main(post_data):
    post_data = dict(x.split(":") for x in post_data.split("\n"))
    URL = 'http://www.urogene.org/cgi-bin/methprimer/methprimer_results.cgi'

    import urllib
    html = urllib.urlopen(URL, urllib.urlencode(post_data)).read()
    if 'No primers found!' in html:
        raise StopIteration

    lines = [x.strip() for x in html.split("Sequence Length:")[1].split("\n")]
    lefts = ["Left " + l.split("</a>")[1].strip() for l in lines if ">Left</a>" in l]
    rights = [l for l in lines if "Right primer" in l and not "<<<" in l]
    products = [l for l in lines if "Product size:" in l]
    assert len(lefts) == len(rights) == len(products)

    lefts = [re.split(SPACES, l) for l in lefts]
    rights = [re.split(SPACES, r) for r in rights]
    products = [re.split(SPACES, p) for p in products]

    for lrp in zip(lefts, rights, products):
        yield lrp

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description=__doc__,
                   formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--primer-size", dest="primer_size", help="range of primer"
            " sizes. format is min:optimal:max   e.g.  %(default)s",
            default="18:25:30")
    p.add_argument("--product-size", dest="product_size", help="range of "
            "product sizes. format is min:optimal:max   e.g.  %(default)s",
            default="180:220:300")
    p.add_argument("--temp-range", dest="temp_range", help="range of "
            "temperatures sizes. format is min:optimal:max   e.g.  %(default)s",
            default="52:60:74")

    p.add_argument("fasta", help="fasta containing regions")

    args = p.parse_args()
    pmin, popt, pmax = map(int, args.primer_size.split(":"))
    prod_min, prod_opt, prod_max = map(int, args.product_size.split(":"))
    tmin, topt, _tmax = map(int, args.temp_range.split(":"))

    print  "\t".join(COLUMNS)
    for header, seq in fasta_iter(args.fasta):
        if header.endswith("/2"): continue
        seen = {}
        tmax = min(_tmax, len(seq))
        for lrp in main(post_data % locals()):
            line = [header]
            left, right, product = lrp
            line.extend(product + left[1:] + right[1:])
            s = "\t".join(line)
            if s in seen: continue
            seen[s] = True
            print s
