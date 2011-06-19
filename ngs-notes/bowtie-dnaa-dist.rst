
`Bao et al`_ found in a recent paper that bowtie maps only 0.02% of reads in
paired end mode. I wanted to see why that was the case.
As they did, I generated paired-end reads with `dnaatools`_ *dwgsim*
The command I used was::

    dwgsim -d 300 -s 50 -N 10000 -1 76 -2 76 chr22.fa gen gen

Indicating that the distance between ends should be 300 bp on average with 
a standard deviation of 50. Since this is just a test, I use human chromosome
22 and generate only 10000 reads.

I then create the bowtie index as they do in the paper::


    ./bowtie/bowtie-0.12.7/bowtie-build chr22.fa chr22

And then map with the sam parameters they do (except I output SAM format and use 4 processors instead of 1)::

    ./bowtie/bowtie-0.12.7/bowtie -v2 --sam -p 4 chr22 -1 gen.bwa.read1.fastq -2 gen.bwa.read2.fastq out0.sam


The output from this is::


    # reads processed: 10000
    # reads with at least one reported alignment: 10 (0.10%)
    # reads that failed to align: 9990 (99.90%)
    Reported 10 paired-end alignments to 1 output stream(s)



**Indeed** as reported in the paper, there is a very low mapping rate.
The reason this occurs is because they did not specify the maximum insert
size...
From the bowtie docs::


    The maximum insert size for valid paired-end alignments. 
    E.g. if -X 100 is specified and a paired-end alignment consists
    of two 20-bp alignments in the proper orientation with a 60-bp
    gap between them, that alignment is considered valid (as long
    as -I is also satisfied). A 61-bp gap would not be valid in that
    case. If trimming options -3 or -5 are also used, the -X constraint
    is applied with respect to the untrimmed mates, not the trimmed
    mates. Default: 250.

So the reads are 76 and dwgsim uses the distance specified (here 300)
as the outer dist then bowtie *should* map with the default maxins of 
250. However, clearly it does not. If we assume it's actually measuring
the inner distance, then we need 300 + 76 * 2 + 2* standard-deviation 
-- so we'll just use 700::


    ./bowtie/bowtie-0.12.7/bowtie --maxins 700 -v2 --sam -p 4 chr22 -1 gen.bwa.read1.fastq -2 gen.bwa.read2.fastq out.sam

The output from this is::

    # reads processed: 10000
    # reads with at least one reported alignment: 6405 (64.05%)
    # reads that failed to align: 3595 (35.95%)
    Reported 6405 paired-end alignments to 1 output stream(s)

So that maps 64% of reads and that can be increased by allowing more
mismatches. So, this is either an error in the docs.
If we create a .bam file::

    samtools view -h -bS out.sam | samtools sort - out

and check it with picard tools::

    java -jar src/picard/picard-tools-1.39/CollectInsertSizeMetrics.jar I=out.bam O=out.txt H=out.hist ASSUME_SORTED=true

we can see the insert size distribution:


.. image:: https://github.com/brentp/bio-playground/raw/master/ngs-notes/images/insert-size.png


So it is actually centered around 450. So dnaa tools is generating pairs
with an **inner** distance specified by `-d` not the **outer** distance as
advertised.


.. _`Bao et al`: http://www.nature.com/jhg/journal/vaop/ncurrent/full/jhg201143a.html
.. _`dnaatools`: http://sourceforge.net/apps/mediawiki/dnaa/index.php?title=Main_Page
