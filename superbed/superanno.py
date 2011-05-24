"""
    %prog [options] files
"""
import optparse
import sys
from pybedtools import BedTool
import collections


def nopen(f, mode="rb"):
    return {"r": sys.stdin, "w": sys.stdout}[mode[0]] if f == "-" \
         else open(f, mode)


def reader(fname, header=True, sep="\t"):
    r"""
    for each row in the file `fname` generate dicts if `header` is True
    or lists if `header` is False. The dict keys are drawn from the first
    line. If `header` is a list of names, those will be used as the dict
    keys.
    """
    fh = nopen(fname)
    line_gen = (l.rstrip("\r\n").split(sep) for l in fh)
    if header == True:
        header = line_gen.next()
        header[0] = header[0].lstrip("#")

    if header:
        for toks in line_gen:
            d = dict(zip(header, toks))
            yield d
    else:
        for toks in line_gen:
            yield toks

def simplify_bed(fbed, has_header):
    """
    create a bed with no header and 6 columns.
    retain strand info.
    """
    line_gen = reader(fbed, header=False)
    header = line_gen.next() if has_header else None
    fh = open(BedTool._tmp(), "w")
    for toks in line_gen:
        new_toks = toks[:3] + ["Z_Z".join(toks), ".", toks[5]]
        fh.write("\t".join(new_toks) + "\n")
    fh.close()
    return BedTool(fh.name), header

def overlapping(a, b):
    by_name = collections.defaultdict(list)
    for row in a.intersect(b, wo=True).cut(range(6) + [9, 10]):
        by_name[row[3]].append((row))
    fh = open(BedTool._tmp(), "w")
    for name, rows in by_name.iteritems():
        types = sorted(set([r[7] for r in rows]))
        # TODO: associate the name with the feature-type.
        full_names = sorted(set([r[6] for r in rows]))
        #regain the original line.
        line = name.split("Z_Z") + [";".join(full_names), ";".join(types)]
        fh.write("\t".join(line) + "\n")
    fh.close()
    return fh.name

def nearest(a, b):
    a_not_overlapping = a.intersect(b, v=True)
    ab = a_not_overlapping.closest(b, t="all")
    fh = open(BedTool._tmp(), "w")
    for row in ab:
        fields = row.fields
        astart, aend = row.start, row.end
        print fields
        bstart, bend = int(fields[7]), int(fields[8])
        # TODO: handle ties in distance.
        if bstart > aend:
            dist = bstart - aend
        elif astart > bend:
            dist = astart - bend
        else:
            1/0
        line = row[3].split("Z_Z") + [row[9], str(dist)]
        fh.write("\t".join(line) + "\n")
    fh.close()
    return fh.name

def superanno(abed, bbed, has_header):
    out = sys.stdout
    a, header = simplify_bed(abed, has_header)
    over = overlapping(a, bbed)
    near = nearest(a, bbed)
    if header:
        out.write("\t".join(header + ['gene', 'location']) + "\n")
    for line in open(over):
        out.write(line)
    for line in open(near):
        out.write(line)


def main():
    p = optparse.OptionParser(__doc__)
    p.add_option("-a", dest="a", help="file to annotate. first 3 columns are "
                                      "chrom start stop")
    p.add_option("-b", dest="b", help="superbed to annotate with")

    p.add_option("--header", dest="header", help="a file has a header",
                    action="store_true", default=False)

    opts, args = p.parse_args()
    if (opts.a is None or opts.b is None):
        sys.exit(not p.print_help())

    superanno(opts.a, opts.b, opts.header)


if __name__ == "__main__":
    import doctest
    if doctest.testmod(optionflags=doctest.ELLIPSIS |\
                                   doctest.NORMALIZE_WHITESPACE).failed == 0:
        main()
