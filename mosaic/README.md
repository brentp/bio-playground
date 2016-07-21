Find mosaic variants.

Rules
=====

+ the parents have 0 alternate alleles
+ the kid has >= 2 alternate alleles

These include sites where the kid is likely to be called as homozygous reference
and would be missed with normal variant calling method.

Usage
=====

```
python mosaic.py $region $ped $fasta $bams
```

e.g.

```
python mosaic.py 9:135766735-135820020 my.ped hs37d5.fa /path/to/*.bam
```

Requirements
============

+ Samples names in the ped must match the read-groups in the bam.
+ Freebayes must be installed
+ peddy python module must be installed

This will only run on **trios** specified in the ped file. It will

It will output a VCF from freebayes with only candidate mosaic variants
in any of the kids. It adds a `MOSAIC` field to the info that indicates
which sample has evidence of mosaicism, and what are the ref and alt counts
and what are the sum of alternate quality score, e.g.:

```
MOSAIC=sample_z42:114:3:33;...
```

where here, `sample_z42` has 114 reference alleles and 3 alternate alles with a total
sum quality of 33. So this candidate will likely be filtered downstream.

If there are multiple probands that are candidates for mosaicism at this site, they
will be delimited by "|".
