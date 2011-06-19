Annotate a Bed File
===================

Given a file in some kind of bed format (at least the first 3 cols are chr start end),
generate a new file with 2 extra columns: gene, distance.
In cases where the distance is zero, the feature type(s) where the overlap occured is 
reported. These could be introns/exons/utrs, etc.

Example Workflow
================
Get the data from UCSC (or your local mirror).
::

    ORG=hg19
    mysql -D $ORG -e "select chrom,txStart,txEnd,cdsStart,cdsEnd,K.name,X.geneSymbol,proteinID,strand,exonStarts,exonEnds from knownGene as K,kgXref as X where  X.kgId=K.name" > $ORG.notbed

Check the actual command in UCSC if you do not have a local DB set up.


create a bed6 file with a line for each column::

    python superbed.py $ORG.notbed > $ORG.super.bed


install `bedtools`_ and `pybedtools`_

annotate some data with `superanno.py`::

    python superanno.py -a my.bed -b $ORG.super.bed --header > my.annotated.bed

my.annotated.bed will now have 2 extra columns: gene(s), distance/feature_type.
