from __future__ import print_function
import sys
from geneimpacts import VEP


def isfunctional(csq):
    if csq['BIOTYPE'] != 'protein_coding': return False
    if csq['Feature'] == '' or csq['EXON'] == '': return False
    return any(c in ('stop_gained', 'stop_lost', 'start_lost', 'initiator_codon_variant', 'rare_amino_acid_variant',
                     'missense_variant', 'protein_altering_variant', 'frameshift_variant')
                 for c in csq['Consequence'].split('&'))

for line in sys.stdin:
    if line[0] == "#":
        print(line, end="")
        continue

    toks = line.rstrip().split("\t")
    info = toks[7]
    pos = info.index('CSQ=') + 4

    vi = info[pos:].split(";")[0]

    veps = [VEP(c) for c in vi.split(",")]

    if not any(isfunctional(v) for v in veps):
        continue

    if 'max_aaf_all=' in info:
        vals = info.split('max_aaf_all=')[1].split(";")[0].split(",")
        if max(map(float, vals)) > 0.001:
            print("skipping because of max_aaf_all:", line, file=sys.stderr)
            continue

    print(line, end="")
