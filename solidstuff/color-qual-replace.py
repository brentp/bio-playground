#!/usr/bin/env python
"""
Color aware aligners (BFAST, Shrimp, ...) output color base-qualities in the
'CQ:Z' tag. Variant callers will ignore this.
This script replaces the existing base-quality (column 11) with the color-base
quality in the CQ:Z tag (if it exists)
reads from stdin and writes to stdout. usage like:

  $ samtools view -h input.bam | python color-qual-replace.py \
          | samtools view -bS - > output.bam
"""
import sys

for line in sys.stdin:
    if line[0] == "@" or not "CQ:Z:" in line: print line,
    else:
        toks = line.rstrip("\r\n").split("\t")
        for t in toks[11:]:
            if t.startswith("CQ:Z:"):
                toks[10] = t[5:]
                break
        else:
            raise Exception("BAD")

        print "\t".join(toks)
