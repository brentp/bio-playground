"""
    %prog [options] files
"""
import optparse
import sys
from pybedtools import BedTool
import collections
from toolshed import reader

def simplify_bed(fbed, has_header):
    """
    create a bed with no header and 6 columns.
    retain strand info.
    """
    line_gen = reader(fbed, header=False)
    header = line_gen.next() if has_header else None
    fh = open(BedTool._tmp(), "w")
    for toks in line_gen:
        new_toks = toks[:3] + ["Z_Z".join(toks), "."]
        # strand...
        if len(toks) > 5 and toks[5] in "+=":
            new_toks.append(toks[5])
        fh.write("\t".join(new_toks) + "\n")
    fh.close()
    return BedTool(fh.name), header

def xstream(a, b, distance, updown, out):
    """
    find all things in b that are within
    distance of a in the given direction
    (up or down-stream)
    """
    direction = dict(u="l", d="r")[updown[0]]
    kwargs = {'sw':True, direction: distance}

    if "l" in kwargs: kwargs["r"] = 0
    else: kwargs["l"] = 0
    a = BedTool(a).saveas()

    kwargs['stream'] = True
    c = a.window(b, **kwargs)
    afields = a.field_count()

    seen = collections.defaultdict(set)
    for feat in c:
        key = "\t".join(feat[:afields])
        # keep track of all the feature names that overlap this one
        seen[key].update((feat[afields + 3],))

    # the entries that did appear in the window
    for row in seen:
        out.write(row + "\t" + ",".join(sorted(seen[row])) + "\n")

    # write the entries that did not appear in the window'ed Bed
    for row in a:
        key = "\t".join(row[:afields])
        if key in seen: continue
        out.write(str(row) + "\t.\n")
    out.flush()
    assert len(BedTool(out.name)) == len(a)

def overlapping(a, b):
    by_name = collections.defaultdict(list)
    for row in a.intersect(b, wo=True, stream=True).cut(range(6) + [9, 10],
            stream=True):
        key = row[3] # the ZZ joined string.
        # 6, 7 are name, type.
        by_name[key].append((row[6], row[7]))

    fh = open(BedTool._tmp(), "w")
    for name, rows in by_name.iteritems():
        types = sorted(set([r[1] for r in rows]))
        full_names = sorted(set([r[0] for r in rows]))
        #regain the original line.
        line = name.split("Z_Z") + [";".join(full_names), ";".join(types)]
        fh.write("\t".join(line) + "\n")
    fh.close()
    return fh.name

def nearest(a, b):
    a_not_overlapping = a.intersect(b, v=True)
    if len(a_not_overlapping) != 0:
        ab = a_not_overlapping.closest(b, t="all", stream=True)
    else:
        ab = []

    by_name = collections.defaultdict(list)
    for row in ab:
        key = row[3]
        row[3] = "."
        by_name[key].append(row)

    fh = open(BedTool._tmp(), "w")
    seen = set()

    for name, rows in by_name.iteritems():
        # TODO: just like above.
        full_names = [r[9] for r in rows]

        dists = [get_dist(r) for r in rows]
        if len(set(dists)) == 1:
            dists = set(dists)
            full_names = set(full_names)
        dists = ";".join(map(str, dists))
        names = ";".join(full_names)

        line = "\t".join(name.split("Z_Z") + [names, dists])
        if line in seen: continue
        seen.add(line)
        fh.write(line + "\n")
    fh.close()
    return fh.name

def get_dist(row):
    fields = row.fields
    astart, aend = row.start, row.end
    bstart, bend = int(fields[7]), int(fields[8])
    # TODO: handle ties in distance.
    if bstart >= aend:
        dist = (bstart - aend) + 1
    elif astart >= bend:
        dist = bend - astart
    else:
        1/0
    return dist

def superanno(abed, bbed, has_header, out=sys.stdout):
    a, header = simplify_bed(abed, has_header)
    over = overlapping(a, bbed)
    near = nearest(a, bbed)
    if header:
        out.write("\t".join(header + ['gene', 'location']) + "\n")
    for line in open(over):
        out.write(line)
    for line in open(near):
        out.write(line)

def remove_transcripts(b):
    bnew = open(BedTool._tmp(), "w")
    for row in reader(b, header=False):
        if "," in row[3]:
            row[3] = row[3].split(",")[1]
        bnew.write("\t".join(row) + "\n")
    bnew.close()
    return bnew.name

def main():
    p = optparse.OptionParser(__doc__)
    p.add_option("-a", dest="a", help="file to annotate. first 3 columns are "
                                      "chrom start stop")
    p.add_option("-b", dest="b", help="superbed to annotate with")

    p.add_option("--header", dest="header", help="a file has a header",
                    action="store_true", default=False)

    p.add_option("--upstream", dest="upstream", type=int, default=None,
                   help="distance upstream of [a] to look for [b]")
    p.add_option("--downstream", dest="downstream", type=int, default=None,
                   help="distance downstream of [a] to look for [b]")
    p.add_option("--transcripts", dest="transcripts", action="store_true",
            default=False, help="use transcript names in output as well as"
            " gene name. default is just gene name")

    opts, args = p.parse_args()
    if (opts.a is None or opts.b is None):
        sys.exit(not p.print_help())

    b = opts.b
    if not opts.transcripts:
        b = remove_transcripts(b)

    if not (opts.upstream or opts.downstream):
        superanno(opts.a, b, opts.header, sys.stdout)

    else:
        out = open(BedTool._tmp(), "w")
        superanno(opts.a, b, opts.header, out)
        out.close()

        new_header = []
        out_fh = open(out.name)
        new_header = [out_fh.readline().rstrip("\r\n")] if opts.header else []
        for xdir in ("upstream", "downstream"):
            dist = getattr(opts, xdir)
            if dist is None: continue
            new_out = open(BedTool._tmp(), "w")
            xstream(out_fh, b, dist, xdir, new_out)
            new_header.append("%s_%i" % (xdir, dist))
            new_out.close()
            out_fh = open(new_out.name)

        if opts.header:
            print "\t".join(new_header)
        for line in open(out_fh.name):
            sys.stdout.write(line)

if __name__ == "__main__":
    import doctest
    if doctest.testmod(optionflags=doctest.ELLIPSIS |\
                                   doctest.NORMALIZE_WHITESPACE).failed == 0:
        main()
