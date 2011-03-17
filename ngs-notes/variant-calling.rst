Variant Calling
===============

First perform `realignment`

Calling on All Samples / Using Read Groups
------------------------------------------


    + add a read group to BAM/SAM: http://seqanswers.com/forums/showthread.php?t=4180

        * ID = id name for the readgroup
        * SM = sample name
        * LB = label? dunno about this one
        * PL = platform (Illumina/SoLid/etc.)

    + from free-bayes help::

        FreeBayes is designed to be run on many individuals from the same population
        (e.g. many human samples) simultaneously.  The algorithm exploits a neutral
        model of evolution and allele diffusion to impute most-confident genotypings
        across the entire population.  In practice, the quality and confidence in the
        callset will increase if you run multiple samples simultaneously.  If your
        study has multiple individuals, you should run freebayes against them at the
        same time.

        To call variants in a population of samples, each alignment must have a read
        group identifier attached to it (RG tag), and the header of the BAM file in
        which it resides must map the RG tags to sample names (SM).  Furthermore, read
        group IDs must be unique across all the files used in the analysis.

    + from samtools spec:  @RG Read group. Unordered multiple lines are allowed.

        * **ID** Read group identifier. Each @RG line must have a unique ID. The value of ID is used in the RG tags of alignment records. Must be unique among all read groups in header section. Read group IDs may be modifieded when merging SAM filles in order to handle collisions.

         * **CN** Name of sequencing center producing the read.

         * **DS** Description.

         * **DT** Date the run was produced (ISO8601 date or date/time).  LB Library.

         * **PG** Programs used for processing the read group.

         * **PI** Predicted median insert size.

         * **PL** Platform/technology used to produce the read. Valid values: ILLUMINA, SOLID, LS454, HELICOS and PACBIO.

         * **PU** Platform unit (e.g. flowcell-barcode.lane for Illumina or slide for SOLiD). Unique identifier.

         * **SM** Sample. Use pool name where a pool is being sequenced.


    + example

        * header: @RG\tID:some-unique-id\tSM:hs\tLB:ga\tPL:Illumina

        * in a single read: RG:Z:some-unique-id

    + from samtools mpileup docs::

        "One alignment file can contain multiple samples; reads from one sample
        can also be distributed in different alignment files. SAMtools will regroup
        the reads anyway. In addition, if no @RG lines are present, each
        alignment file is taken as one sample."

    + also see: http://www.broadinstitute.org/gsa/wiki/index.php/Frequently_Asked_Questions#My_BAM_file_doesn.27t_have_read_group_and_sample_information.__Do_I_really_need_it.3F

Parameters
----------

    U87MG Decoded paper: phred score >= 10, observed >=4 times and <= 60 times. and 1x per strand.


GATK
----

  http://www.broadinstitute.org/gsa/wiki/index.php/The_Genome_Analysis_Toolkit#Variant_Discovery_Tools

  http://www.broadinstitute.org/gsa/wiki/index.php/Indel_Genotyper_V2.0

  http://www.broadinstitute.org/gsa/wiki/index.php/Unified_genotyper#Indel_Calling_with_the_Unified_Genotyper


FreeBayes
---------

  https://github.com/ekg/freebayes

Samtools
--------

    http://lh3lh3.users.sourceforge.net/download/multigeno.pdf

    http://samtools.sourceforge.net/samtools.shtml

    ::

        # but use -B to avoid realignment if already called  samtools calmd
        $ samtools mpileup -m 4 -F 0.2 -C 50 -D -S -gf hg19.fa a.bam b.bam c.bam > ${out}.all.pileup

        $ bcftools view -bvcg out.pileup > ${out}.all.vcf
        $ bcftools view ${out}.all.vcf | vcfutils.pl varFilter -D100  -d 3 **[discuss other opts]** > ${out}.vcf

References
----------

    + Homer N, Nelson SF. 2010. Improved variant discovery through local re-alignment of short-read next-generation sequencing data use SRMA. Genome Biology. 11:R99.
