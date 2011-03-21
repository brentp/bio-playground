"""
    %prog [options] files

plot a manhattan plot of the input file(s).
"""

import optparse
import sys
from itertools import groupby, cycle
from operator import itemgetter
from matplotlib import pyplot as plt
import numpy as np

def _gen_data(fhs, columns, sep):
    """
    iterate over the files and yield chr, start, pvalue
    """
    for fh in fhs:
        for line in fh:
            if line[0] == "#": continue
            toks = line.split(sep)
            yield toks[columns[0]], int(toks[columns[1]]), float(toks[columns[2]])

def chr_cmp(a, b):
    a = a.lower().replace("_", ""); b = b.lower().replace("_", "")
    achr = a[3:] if a.startswith("chr") else a
    bchr = b[3:] if b.startswith("chr") else b

    try:
        return cmp(int(achr), int(bchr))
    except ValueError:
        if achr.isdigit() and not bchr.isdigit(): return -1
        if bchr.isdigit() and not achr.isdigit(): return 1
        # X Y
        return cmp(achr, bchr)


def chr_loc_cmp(alocs, blocs):
    return chr_cmp(alocs[0], blocs[0]) or cmp(alocs[1], blocs[1])



def manhattan(fhs, columns, image_path, no_log, colors, sep, title, lines, ymax):

    xs = []
    ys = []
    cs = []
    colors = cycle(colors)
    xs_by_chr = {}

    last_x = 0
    data = sorted(_gen_data(fhs, columns, sep), cmp=chr_loc_cmp)

    for seqid, rlist in groupby(data, key=itemgetter(0)):
        color = colors.next()
        rlist = list(rlist)
        region_xs = [last_x + r[1] for r in rlist]
        xs.extend(region_xs)
        ys.extend([r[2] for r in rlist])
        cs.extend([color] * len(rlist))

        xs_by_chr[seqid] = (region_xs[0] + region_xs[-1]) / 2

        # keep track so that chrs don't overlap.
        last_x = xs[-1]

    xs_by_chr = [(k, xs_by_chr[k]) for k in sorted(xs_by_chr.keys(), cmp=chr_cmp)]

    xs = np.array(xs)
    ys = np.array(ys) if no_log else -np.log10(ys)

    plt.close()
    f = plt.figure()
    ax = f.add_axes((0.1, 0.09, 0.88, 0.85))

    if title is not None:
        plt.title(title)

    ax.set_ylabel('-log10(p-value)')
    if lines:
        ax.vlines(xs, 0, ys, colors=cs, alpha=0.5)
    else:
        ax.scatter(xs, ys, s=2, c=cs, alpha=0.8, edgecolors='none')

    # plot 0.05 line after multiple testing.
    ax.axhline(y=-np.log10(0.05 / len(data)), color='0.5', linewidth=2)
    plt.axis('tight')
    plt.xlim(0, xs[-1])
    plt.ylim(ymin=0)
    if ymax is not None: plt.ylim(ymax=ymax)
    plt.xticks([c[1] for c in xs_by_chr], [c[0] for c in xs_by_chr], rotation=-90, size=8.5)
    print >>sys.stderr, "saving to: %s" % image_path
    plt.savefig(image_path)
    #plt.show()


def get_filehandles(args):
    return (open(a) if a != "-" else sys.stdin for a in args)


def main():
    p = optparse.OptionParser(__doc__)
    p.add_option("--no-log", dest="no_log", help="don't do -log10(p) on the value",
            action='store_true', default=False)
    p.add_option("--cols", dest="cols", help="zero-based column indexes to get"
        " chr, position, p-value respectively e.g. %default", default="0,1,2")
    p.add_option("--colors", dest="colors", help="cycle through these colors",
                default="bk")
    p.add_option("--image", dest="image", help="save the image to this file. e.g. %default",
                default="manhattan.png")
    p.add_option("--title", help="title for the image.", default=None, dest="title")
    p.add_option("--ymax", help="max (logged) y-value for plot", dest="ymax", type='float')
    p.add_option("--sep", help="data separator, default is [tab]",
            default="\t", dest="sep")
    p.add_option("--lines", default=False, dest="lines", action="store_true",
        help="plot the p-values as lines extending from the x-axis rather than"
             " points in space. plotting will take longer with this option.")

    opts, args = p.parse_args()
    if (len(args) == 0):
        sys.exit(not p.print_help())
    fhs = get_filehandles(args)
    columns = map(int, opts.cols.split(","))
    manhattan(fhs, columns, opts.image, opts.no_log, opts.colors, opts.sep,
            opts.title, opts.lines, opts.ymax)


if __name__ == "__main__":
    main()
