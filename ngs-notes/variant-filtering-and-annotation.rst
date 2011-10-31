Filtering
=========

    + Most tools create or expect Variant Call Format: `VCF`_

    + From there, `VCFTools`_ can be used to:

        *  filter on
            - quality
            - depth
            - allele frequency
            - etc.

        * summarize
            - frequency
            - depth
            - quality
            - etc.


    + other tools:

        * `vcflib`_

        * solid-gff3-to-vcf.py will convert solid output to `VCF`_
          with filters for coverage and quality.

Annotation
==========

    + `Annovar`_ (Command-Line) :

        * Annotates based on:
            - genes: refGene / Known Gene / EnsGene
            - any track from UCSC
            - dbsnp phastCons segdups, etc.
        * Run from command-line like

            - annotate based on location in/near gene (exon/intron/up/down)::

                $ ./annotate_variation.pl --buildver hg19 --geneanno $INPUT humandb/

            - annotate based on presence in dbsnp::

                $ ./annotate_variation.pl --buildver hg19 --filter --dbtype 1000g2010nov_all ${IN} humandb

    + `SeattleSeq`_ (Web-Based):

        * seems to have no limit on query size.

        * requires choosing a single individual from dbSNP

        * outputs columns of:

			- inDBSNPOrNot
			- chromosome
			- position
			- referenceBase
			- sampleGenotype
			- sampleAlleles
			- dbSNPGenotype
			- allelesDBSNP
			- accession
			- functionGVS
			- functionDBSNP
			- rsID
			- aminoAcids
			- proteinPosition
			- polyPhen
			- scorePhastCons
			- consScoreGERP
			- chimpAllele
			- CNV
			- geneList
			- AfricanHapMapFreq
			- EuropeanHapMapFreq
			- AsianHapMapFreq
			- hasGenotypes
			- dbSNPValidation
			- repeatMasker
			- tandemRepeat
			- clinicalAssociation
			- distanceToSplice
			- microRNAs
			- proteinSequence

    + `snpEff`_ (Command-line)

        * Annotates based on Ensembl genes (up/downstream, intron, utr, exon)

        * For exon reports:

            - non/synonymous
            - stop/start codon gain/lost
            - splice/frame shift

    + `bedtools`_ (Command-line)

        * download whatever data you want. get it it bed/gff format and
          use linux commands like cut to get desired columns.

Suggested Short-Term Pipeline
=============================

    + convert solid gff3 to vcf

    + filter out snps in dbsnp

        * use VCF from dbsnp and vcftools

        * **discuss parameters** (e.g. frequency in dbsnp)

    + **discuss** filter out those near centromere??

    + Annotate remaining with `SeattleSeq`_

        * Most are non-coding

        * **discuss what to do with these**

    + annotate based on various UCSC tracks with `Annovar`_

    + view in UCSC with automatic links.
      ( SchwartzHuman/brentp/annotate-variants/annovar-to-ucsc-bed.py )

Suggested Mid-Term Pipeline
===========================


    + add read-groups for individuals

      - combine all bams

    + remove dups (dnaatools or picard markDuplicates)

    + samtools calmd (parallelized by chromsome)

    + free-bayes (parallelized by chromsome)


Suggested Long-Term Pipeline
============================

    + Use BFast Alignments

    + remove dups (dnaatools or picard markDuplicates)

    + SRMA to do local re-alignment

    + samtools calmd

    + Indel calling:

        + samtools mpileup

        + freebayes


.. _`VCF`: http://vcftools.sourceforge.net/specs.html
.. _`VCFTools`: http://vcftools.sourceforge.net/options.html
.. _`vcflib`: https://github.com/ekg/vcflib
.. _`Annovar`: http://www.openbioinformatics.org/annovar/
.. _`SeattleSeq`: http://gvs-p.gs.washington.edu/SeattleSeqAnnotation131/index.jsp
.. _`snpEff`: http://snpeff.sourceforge.net
.. _`bedtools`: http://github.com/arq5x/bedtools
