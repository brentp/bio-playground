"""
    %prog [options] filea:col# fileb:col#

join filea with fileb by looking for the same value in col#

col numbers are 0-based indexing.

can never get linux join to work as i want.
"""
import optparse
import sys

def join(fa, cola, fb, colb, sepa, sepb, remove):
    bgen = (line.rstrip("\n") for line in open(fb))
    bdict = dict((line.split(sepb)[colb], line) for line in bgen)
    for line in open(fa):
        toks = line.split(sepa)
        key = toks[cola]
        bstuff = bdict.get(key, "").split(sepb)
        if remove and bstuff:
            del bstuff[colb]
        print line.strip("\r\n") + sepa + sepa.join(bstuff)


def main():
    p = optparse.OptionParser(__doc__)
    p.add_option("--sepa", dest="sepa", default="\t", help="separator for 1st file")
    p.add_option("--sepb", dest="sepb", default="\t", help="separator for 2nd file")
    p.add_option("-x", dest="x", action="store_true", default=False, 
            help="only print the shared column once.")
    opts, args = p.parse_args()
    if (len(args) != 2):
        sys.exit(not p.print_help())
    fa, cola = args[0].split(":")
    fb, colb = args[1].split(":")
    join(fa, int(cola), fb, int(colb), opts.sepa, opts.sepb, opts.x)

if __name__ == "__main__":
    main()
