"""
    %prog [options] filea:col# fileb:col#

e.g.

    %prog --sepa , --sepb , f1.txt:2 f3.txt:5

join filea with fileb by looking for the same value in col#

col numbers are 0-based indexing. can key on multiple columns:

    %prob f1.txt:2:4 f3.txt:5:7

will use columns 2 and 4 and check agains columns 5 and 7.
"""
import optparse
import sys

def join(fa, colsa, fb, colsb, sepa, sepb, remove):
    bgen = (line.rstrip("\n") for line in open(fb))
    bdict = {}
    for line in bgen:
        # can have multiple keys and keep the header in case
        # file a has one also.
        if line[0] == "#":
            bdict['header'] = line[1:]
            continue
        toks = line.split(sepb)
        key = tuple(toks[ib] for ib in colsb)
        bdict[key] = line

    mismatches = 0
    for line in open(fa):
        if line[0] == "#":
            bstuff = bdict.get('header', '').split(sepb)
            if remove:
                for colb in sorted(colsb, reverse=True):
                    del bstuff[colb]
            print line.rstrip("\r\n") + sepa + sepa.join(bstuff)
            continue

        toks = line.split(sepa)
        key = tuple(toks[cola] for cola in colsa)
        bstuff = bdict.get(key, "").split(sepb)
        mismatches += int(bstuff == [''])
        if remove and bstuff and bstuff[0]:
            for colb in sorted(colsb, reverse=True):
                if bstuff != ['']: del bstuff[colb]

        print line.strip("\r\n") + sepa + sepa.join(bstuff)
    print >>sys.stderr, "%i lines did not match" % mismatches

def main():
    p = optparse.OptionParser(__doc__)
    p.add_option("--sepa", dest="sepa", default="\t", help="separator for 1st file")
    p.add_option("--sepb", dest="sepb", default="\t", help="separator for 2nd file")
    p.add_option("-x", dest="x", action="store_true", default=False, 
            help="only print the shared column once.")
    opts, args = p.parse_args()
    if (len(args) != 2):
        sys.exit(not p.print_help())
    a = args[0].split(":")
    fa, colsa = a[0], a[1:]
    b = args[1].split(":")
    fb, colsb = b[0], b[1:]

    join(fa, map(int, colsa), fb, map(int, colsb), opts.sepa, opts.sepb, opts.x)

if __name__ == "__main__":
    main()
