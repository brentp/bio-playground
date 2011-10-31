Problem Alignments
==================

  From samtools docs::

    The following shows the alignments of 6 reads by a typical read mapper in
    the presence of a 4bp homozygous INDEL:

         coor     12345678901234    5678901234567890123456
         ref      aggttttataaaac----aattaagtctacagagcaacta
         sample   aggttttataaaacAAATaattaagtctacagagcaacta
         read1    aggttttataaaac****aaAtaa
         read2     ggttttataaaac****aaAtaaTt
         read3         ttataaaacAAATaattaagtctaca
         read4             CaaaT****aattaagtctacagagcaac
         read5               aaT****aattaagtctacagagcaact
         read6                 T****aattaagtctacagagcaacta

     where capital bases represent differences from the reference and underlined
     bases are the inserted bases. The alignments except for read3 are wrong
     because the 4bp insertion is misplaced. The mapper produces such alignments
     because when doing a pairwise alignment, the mapper prefers one or two
     mismatches over a 4bp insertion. What is hurting more is that the wrong
     alignments lead to recurrent mismatches, which are likely to deceive most
     site-independent SNP callers into calling false SNPs.


from SRMA paper::

    These local misalignments lead to false positive variant detection, especially at apparent
    heterozygous positions.

Relations explained by Nils Homer: http://seqanswers.com/forums/showpost.php?p=34937&postcount=2::

    Samtools does re-alignment (BAQ) via the forward-backward algorithm using the a
    single read and the reference. SRMA/Dindel/etc use all reads across a given loci.
    The former really helps identify parts of the alignment that are ambiguous (it could
    have been an indel or a snp, but I don't know which one), while the latter class of
    algorithms try to better identify variants from with the read. The BAQ really helps,
    and so does SRMA/Dindel; it's up to you to choose which you like and in what
    combination.

    GATK's base quality score recalibration is explained in the introduction in the link.

Solutions
=========

These are done after the original alignment. Help prevent
false variant discovery due to alignment artifacts.

    + **Base Alignment Quality** (BAQ) adjustment

      - e.g. samtools calmd (takes BAM, returns adjusted BAM,
        see recent paper: Improving SNP discovery by base alignment quality)

      - less computationally intensive

      - doesn't "fix" alignment but avoids false positives


    + **Local Re-alignment** (also discussed by CompleteGenomics guy)

      - e.g. SRMA (takes BAM, returns adjust BAM)

      - more computationally intensive

      - fixes alignment -- improves indel calling

      - also done in GATK: http://sourceforge.net/apps/mediawiki/samtools/index.php?title=SAM_protocol#Support_Protocol_2:_Local_Realignment

BAQ Adjustment (samtools calmd formerly fillmd)
-----------------------------------------------

from samtools docs::

    [samtools calmd] assigns each base a BAQ which is the Phred-scaled probability
    of the base being misaligned. BAQ is low if the base is aligned to a different
    reference base in a suboptimal alignment, and in this case a mismatch should
    contribute little to SNP calling even if the base quality is high. With BAQ, the
    mismatches in the example above are significantly downweighted. SAMtools will
    not call SNPs from that.

usage is::

    samtools calmd -Abr in.bam ref.fasta > out.baq.bam

where flags indicate:

    + `-A` : modify quality string
    + `-r` : do realignment
    + `-b` : output compressed BAM.

The resulting BAM file can used by any downstream snp callers including
the one in samtools or free-bayes (or presumably the solid snp caller).

The BAM file has the MD field, which indicates mismatches in the alignment.
This allows down-stream tools to do indel calling without looking at the
reference.


Also, similar procedure in GATK called Base Quality Recalibration: http://sourceforge.net/apps/mediawiki/samtools/index.php?title=SAM_protocol#Support_Protocol_1:_Base_Quality_Recalibration

and see: http://www.broadinstitute.org/gsa/wiki/index.php/Base_quality_score_recalibration#Introduction

Local Realingment (SRMA)
------------------------

  http://sourceforge.net/apps/mediawiki/srma/index.php?title=Main_Page

  http://genomebiology.com/2010/11/10/R99

  http://sourceforge.net/apps/mediawiki/srma/index.php?title=User_Guide

Example of effect (stolen from SRMA project page).

.. image :: http://sourceforge.net/apps/mediawiki/srma/nfs/project/s/sr/srma/thumb/e/ee/ALPK2_alignments.png/800px-ALPK2_alignments.png


from project page::

    Sequence alignment algorithms examine each read independently. When indels occur towards the ends of reads, the alignment can lead to false SNPs as well as improperly placed indels. This tool aims to perform a re-alignment of each read to a graphical representation of all alignments within a local region to provide a better overall base-resolution consensus.

**works on colorspace**


1000g
-----

ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/README.alignment_data#bam-improvement-section

 + local realignment with GATK

 + mate-pair fix and coordinate sorting with picard

 + read qualities re-calibrated with GATK

 + samtools calmd -r


References
----------

    + Homer N, Nelson SF. 2010. Improved variant discovery through local re-alignment of short-read next-generation sequencing data use SRMA. Genome Biology. 11:R99.

    + Li H, Handsaker B, Wysoker A, Fennell T, Ruan J, Homer N, Marth G, Abecasis G, Durbin R and 1000 Genome Project Data Processing Subgroup. 2009. The Sequence alignment/map (SAM) format and SAMtools. Bioinformatics. 25:2078-9

    + Li H. 2011. Improving SNP discovery by base alignment quality. Bioinformatics. doi: 10.1093/bioinformatics/btr076
