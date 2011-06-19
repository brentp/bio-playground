"""
Separate the data from UCSC into a bed6 file with columns of:

    chrom, start, end, name, type, strand

where type is one of:

        intron, exon, utr5, utr3, utr5_intron, utr3_intron

exon or intron can be prefixed with 'nc_' for non-coding'

Usage:

    %s [options] output.from.ucsc

the file output.from.ucsc can be extracted via mysql::

    mysql --user=genome --host=genome-mysql.cse.ucsc.edu -A -D $ORG -P 3306 \
            -e "SELECT chrom,txStart,txEnd,cdsStart,cdsEnd,K.name,X.geneSymbol,
                proteinID,strand,exonStarts,exonEnds
                FROM knownGene as K,kgXref as X WHERE  X.kgId=K.name" \
                    > output.from.ucsc


where $ORG is something like hg19 or mm8. The header must be present for this to work.
"""
from __future__ import print_function
import sys

def reader(fname, sep="\t"):
    r"""
    for each row in the file `fname` generate dicts based on the header
    in the first row.
    """
    line_gen = (l.rstrip("\r\n").split(sep) for l in open(fname))
    header = line_gen.next()
    header[0] = header[0].lstrip("#")
    for toks in line_gen:
        yield dict(zip(header, toks))

def print_line(start, end, ftype, d):

    if start == end:
        assert "intron" in ftype, ((start, end, ftype, d))
        return
    else:
        assert start < end

    print("%s\t%i\t%i\t%s\t%s\t%s" % (d['chrom'], start, end,
                                      d['full_name'], ftype, d['strand']))

def print_introns(starts_ends, d, ftype="intron"):
    starts, ends = zip(*starts_ends)

    # first possible intron is between end of first and start of 2nd intron.
    for start, end in zip(ends[:-1], starts[1:]):
        print_line(start, end, ftype, d)

def print_exons(starts_ends, d, ftype="exon"):

    if d['cdsStart'] != d['cdsEnd']:
        starts_ends[0][0] = d['cdsStart']
        starts_ends[-1][1] = d['cdsEnd']

    for start, end in starts_ends:
        print_line(start, end, ftype, d)


def print_noncoding_utrs(starts_ends, d, ftype):

    for i, (start, end) in enumerate(starts_ends):
        print_line(start, end, ftype, d)
        if (i + 1) < len(starts_ends):
            intron_start = end
            intron_end = starts_ends[i + 1][0]
            print_line(intron_start, intron_end, ftype + "_intron", d)


def print_features(d):
    starts_ends = zip(d['exonStarts'], d['exonEnds'])
    coding = d['cdsStart'] != d['cdsEnd']
    if coding:
        cds_starts_ends = [[s, e] for (s, e) in starts_ends if s < d['cdsEnd'] \
                                                        and e > d['cdsStart']]

        utr_lefts = [[s, e] for (s, e) in starts_ends \
                                if s < d['cdsStart']]
        utr_rights = [[s, e] for (s, e) in starts_ends \
                                if e > d['cdsEnd']]
        # extend it to the cds start/end.
        if utr_lefts:
            utr_lefts[-1][1] = d['cdsStart']
        if utr_rights:
            utr_rights[0][0] = d['cdsEnd']
            pass

        utr5s = utr_lefts if d['strand'] == '+' else utr_rights
        utr3s = utr_lefts if d['strand'] == '-' else utr_rights

        print_noncoding_utrs(utr5s, d, 'utr5')
        print_noncoding_utrs(utr3s, d, 'utr3')
    else:
        cds_starts_ends = starts_ends


    print_exons(cds_starts_ends, d, "exon" if coding else "nc_exon")
    print_introns(cds_starts_ends, d, "intron" if coding else "nc_intron")


def superbed(ucsc_file):

    for d in reader(ucsc_file):
        for k in ('txStart', 'txEnd', 'cdsStart', 'cdsEnd'):
            d[k] = int(d[k])
        assert d['exonStarts'][-1] == "," == d['exonEnds'][-1]
        d['exonStarts'] =  map(int, d['exonStarts'][:-1].split(","))
        d['exonEnds'] =  map(int, d['exonEnds'][:-1].split(","))
        assert len(d['exonStarts']) == len(d['exonEnds'])
        d['full_name'] = ",".join((d['name'], d['geneSymbol']))
        print_features(d)


def main(args=sys.argv[1:]):
    if len(args) != 1:
        print(__doc__ % sys.argv[0])
        sys.exit(1)

    superbed(args[0])

if __name__ == "__main__":
    import doctest
    if doctest.testmod(optionflags=doctest.ELLIPSIS |\
                                   doctest.NORMALIZE_WHITESPACE).failed == 0:
        main()
