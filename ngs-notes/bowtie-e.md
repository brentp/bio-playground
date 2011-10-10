Using bowtie to map un-ambiguous (colorspace) reads. 
The reason I want to do this is that bowtie is fast. So I want it to:

 * Map reads that are easy--no indels, good quality, etc.
 * Discard reads that map to multiple locations.

This should speed downstream alignment by another *rigorous* but slower downstream aligner.

I want to determine: what's a good cutoff for the sum of qualities of mismatches (`-e`)?

``` sh

for e in 10 30 50 70 90 110 130; do
    bowtie -f -C \
        -Q $QUAL \
        --chunkmbs 1025 --best --sam \
        --max data/rm.e${e}.bowtie.max \
        --un data/rm.e${e}.bowtie.un \
        -n 1 -e ${e} --nomaqround --maxbts 50000 \
        -m 1 -p 8 --seed 42 $REF_COLOR \
        $CSFASTA \
    | samtools view -bSF 4 - > t.e${e}.bam
    
    aligned=$(samtools view -c t.e${e}.bam)
    max=$(grep -c "^>" data/rm.e${e}.bowtie.max)
    echo $e $aligned $max
done
```

Gives:

<table>
<tr>
<th>e</th><th>mapped-reads</th><th>max-reads</th>
</tr><tr>
<td>10</td><td>736383</td><td>16528</td>
</tr><tr>
<td>30</td><td>1238921</td><td>33281</td>
</tr><tr>
<td>50</td><td>1584765</td><td>52277</td>
</tr><tr>
<td>70</td><td>1824751</td><td>73071</td>
</tr><tr>
<td>90</td><td>1979517</td><td>89968</td>
</tr><tr>
<td>110</td><td>2076351</td><td>105399</td>
</tr><tr>
<td>130</td><td>2134483</td><td>118584</td>
</tr>
</table>

The max-reads column tells the number of reads that are excluded because the mapped to more than 1 location in the genome. I'm not sure why this varies so greatly with differing values of `e`.

So, even with allowing only a single mismatch in the seed (first 28 bp by default), the number of
mapped reads varies 3-fold (700K to 2.1M) depending on the allow sum of qualities in the mis-matches.

Even so, bowtie reports `48M` as the cigar string for **every** alignment in all the BAM's above (and a mapping quality of 255 for every alignment).

Since this is for a targetted re-sequencing project, I can check what percentage of the reads are mapping to the target region (65KB) as that varies with the `e` cutoff. But, that is constant (at 96%) regardless of the cutoff.

The question then is how are down-stream variant callers affected by these alignments from bowtie? 
Does the low quality at the mismatches prevent any miscalls? How does BAQ affect this?
