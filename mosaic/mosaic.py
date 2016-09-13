from __future__ import print_function
from argparse import ArgumentParser
from peddy import Ped
import atexit
import subprocess as sp
import sys

def main(args):
    p = ArgumentParser()
    p.add_argument("region")
    p.add_argument("ped")
    p.add_argument("ref")
    p.add_argument("bams", nargs="+")

    a = p.parse_args()

    run(a.ped, a.region, a.ref, a.bams)


MIN_REQ_ALTS = 3
CMD = "freebayes --report-genotype-likelihood-max --genotype-qualities --min-alternate-count {min_req_alts} -B 10 -r {region} -F 0.04 --pooled-continuous -f {ref} {bams}"


def run(pedf, region, ref, bams, min_req_alts=MIN_REQ_ALTS):
    print(pedf, file=sys.stderr)
    ped = Ped(pedf)
    bams = " ".join(bams)

    cmd = CMD.format(**locals())

    sample_names = None

    trios = []
    for f in ped.families.values():
        trios.extend(f.trios(affected=None))
    print("found: %d trios" % len(trios), file=sys.stderr)
    if len(trios) == 0:
        raise Exception("found no trios")

    p = sp.Popen(cmd, shell=True, stderr=sys.stderr, stdout=sp.PIPE)
    atexit.register(p.kill)
    for i, line in enumerate(p.stdout):
        if line[0] == '#':
            if line.startswith("#CHROM"):
                sample_names = line.rstrip().split("\t")[9:]
                print("""##INFO=<ID=MOSAIC,Number=1,Type=String,Description="Pipe-delimited list of samples with evidence of mosaicism">""")

            print(line, end="")
            continue
        toks = line.rstrip().split("\t")
        format = toks[8].split(":")
        if i % 1000 == 0:
            print("mosaic: checked ...", i, file=sys.stderr)
            sys.stderr.flush()

        samples = {sample_names[k]: dict(zip(format, t.split(":"))) for k, t in enumerate(toks[9:])}

        candidates = []
        for kid, mom, dad in trios:
            try:
                mom = samples[mom.sample_id]['AO'].split(",")
                if not any('0' == m for m in mom): continue

                dad = samples[dad.sample_id]['AO'].split(",")
                if not any('0' == d for d in dad): continue

                parents = [mom[k] + dad[k] for k in range(len(dad))]
                if not '00' in parents: continue

                skid = samples[kid.sample_id]
                kid_alts = map(int, skid['AO'].split(","))
            except KeyError: # require all samples to be called.
                continue

            if not any(a >= MIN_REQ_ALTS and parents[k] == '00' for k, a in enumerate(kid_alts)):
                continue

            candidates.append("%s:%s:%s:%s" % (kid.sample_id, skid['RO'], skid['AO'], skid['QA']))
        if not candidates:
            continue

        toks[7] = "MOSAIC=%s;%s" % ("|".join(candidates), toks[7])
        print("\t".join(toks))
        sys.stdout.flush()

if __name__ == "__main__":
    main(sys.argv[1:])
