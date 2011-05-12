#!/usr/bin/python
"""
%prog [options] pair_1.fastq pair_2.fastq

filter reads from paired fastq so that no unmatching reads remain.
output files are pair_1.fastq.trim and pair_2.fastq.trim

see: http://hackmap.blogspot.com/2010/09/filtering-paired-end-reads-high.html
"""
from subprocess import Popen, PIPE
import sys

FASTX_CLIPPER="fastx_clipper"
FASTQ_QUALITY_TRIMMER="fastq_quality_trimmer"

def next_record(fh):
    return [fh.readline().strip() for i in range(4)]

def main(adaptors, M, t, l, fastqs, sanger=False):
    cmds = []
    for fastq in fastqs:
        trim_cmd = "%s -t %i -l %i" % (FASTQ_QUALITY_TRIMMER, t, l)
        if sanger: trim_cmd += " -Q 33"

        clip_cmds = []
        for i, a in enumerate(adaptors):
            if i == 0:
                clip_cmds.append("%s -a %s -M %i -i %s %s" \
                     % (FASTX_CLIPPER, a, M, fastq, "-Q 33" if sanger else ""))
            else:
                clip_cmds.append("%s -a %s -M %i %s" \
                     % (FASTX_CLIPPER, a, M, "-Q 33" if sanger else ""))
        if clip_cmds == []:
            trim_cmd += " -i %s" % fastq

        cmds.append(" | ".join(clip_cmds + [trim_cmd]))
        print "[running]:", cmds[-1]
    procs = [Popen(cmd, stdout=PIPE, shell=True) for cmd in cmds]

    # no temporary file, just read from stdouts.
    fha, fhb = procs[0].stdout, procs[1].stdout
    fhr = open(fastqs[0])
    # strip the /2 or /1 and grab only the headers.
    fhr_headers = (x.strip()[:-2] for i, x in enumerate(fhr) if not (i % 4))

    trima = open("%s.trim" % fastqs[0], 'w')
    trimb = open("%s.trim" % fastqs[1], 'w')
    print >>sys.stderr, "writing %s and %s" % (trima.name, trimb.name)

    ra, rb = next_record(fha), next_record(fhb)
    seen = {}
    for header in fhr_headers:
        seen[header] = True
        if header == ra[0][:-2] == rb[0][:-2]:
            print >>trima, "\n".join(ra)
            print >>trimb, "\n".join(rb)
            ra, rb = next_record(fha), next_record(fhb)

        while ra[0][:-2] in seen:
            ra = next_record(fha)

        while rb[0][:-2] in seen:
            rb = next_record(fhb)

    returncode = 0
    for p in procs:
        p.wait()
        returncode |= p.returncode
    if returncode != 0:
        print >>sys.stderr, "ERROR: non-zero returncode from fastx toolkit"
        sys.exit(returncode)

if __name__ == "__main__":
    import optparse
    p = optparse.OptionParser(__doc__)
    p.add_option("-a", dest="a", help="adaptor sequence to clip seperate multiples with ','", default="")

    p.add_option("-M", dest="M", help="require minimum adapter alignment length of N."
               " If less than N nucleotides aligned with the adapter - don't clip it",
                 default=4, type='int')

    p.add_option("-t", dest="t", help="Quality threshold - nucleotides with lower"
                          " quality will be trimmed (from the end of the sequence ",
                 type='int', default=0)

    p.add_option("-l", dest="l", help="Minimum length - sequences shorter than this (after trimming)"
                                   "will be discarded. Default = 0 = no minimum length.",
                type="int", default=0)
    p.add_option("--sanger", dest="sanger", help="quality scores are ascii 33 sanger encoded (default is 64)", action="store_true")

    opts, fastqs = p.parse_args()
    if not (fastqs and len(fastqs)) == 2:
        sys.exit(p.print_help())

    adaptors = [ad.strip() for ad in opts.a.split(",") if ad.strip()]
    main(adaptors, opts.M, opts.t, opts.l, fastqs, opts.sanger)