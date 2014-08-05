"""
Given a multi-sample VCF, return a matrix of genotypes
"""
from __future__ import print_function, division
import toolshed as ts
import re
import sys


def get_genotype(fmt, gts, gq_cutoff=0):
    splitter = re.compile("/|\|")
    fmt = fmt.split(":")
    ges = []
    gqs = []
    for gt in gts:
        if gt.startswith("./.") or gt == ".":
            ges.append("nan")
            gqs.append('nan')
        else:
            d = dict(zip(fmt, gt.split(":")))
            try:
                g, q = d['GT'], float(d['GQ'])
            except:
                print(fmt, d, file=sys.stderr)
                raise
            gqs.append("%.2f" % q)
            if q < gq_cutoff:
                ges.append("nan")
            else:
                # if multiple ALT's, just set to 1.
                ges.append(sum([min(int(n), 1) for n in splitter.split(g)]))
                if ges[-1] > 2:
                    raise Exception(gt)
                ges[-1] = str(ges[-1])

    assert len(ges) == len(gts)
    return ges, gqs


def main(vcf, gq_cutoff, prefix):
    out_gts = open('{prefix}.gt.txt'.format(prefix=prefix), 'w')
    out_gqs = open('{prefix}.gq.txt'.format(prefix=prefix), 'w')
    for i, d in enumerate(ts.reader(vcf, header="ordered", skip_while=lambda l: l[0] != "#CHROM")):
        if i == 0:
            print("\t".join(["loc"] + d.keys()[9:]), file=out_gts)
            print("\t".join(["loc"] + d.keys()[9:]), file=out_gqs)

        gts, gqs = get_genotype(d['FORMAT'], d.values()[9:], gq_cutoff)
        print("\t".join(["%s:%s" % (d['CHROM'], d['POS'])] + gts), file=out_gts)
        print("\t".join(["%s:%s" % (d['CHROM'], d['POS'])] + gqs), file=out_gqs)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--gq', help='set values with a genotype-quality less than this to NA',
            default=10)
    p.add_argument('vcf')
    p.add_argument('prefix')
    a = p.parse_args()
    print(a.vcf, a.prefix, a.gq)
    main(a.vcf, a.gq, a.prefix)
