import pandas as pd
import numpy as np
import toolshed as ts

xl = pd.ExcelFile('data/nature08516-s4.xls')


gm = xl.parse("Genotype Map", index_col=0)
gm = gm[~np.isnan(gm.start)]

gm.chr = gm.chr.astype(int).astype(str)
gm.chr[gm.chr == "23"] = "X"
gm.start = gm.start.astype(int)
gm.end = gm.end.astype(int)
gm.drop('source', axis=1, inplace=True)
gm.drop('cn', axis=1, inplace=True)
gm.columns = (['#chrom'] + list(gm.columns[1:]))
print(gm.head())

j = gm

def get_bam_lookup(p="data/bam-lookups-from-1kg-site.tsv"):
    l = {}
    for d in ts.reader(p):
        if 'low_coverage' in d['url']: continue
        if 'chr20' in d['url']: continue
        if 'chrom20' in d['url']: continue
        if 'chrom11' in d['url']: continue
        if 'unmapped' in d['url']: continue
        if not d['url'].endswith('.bam'): continue
        if d['Sample'] in l:
            print "XXX:", d['url']
            print "YYY:", l[d['Sample']]
        l[d['Sample']] = d['url']
    return l


samples = get_bam_lookup()

url = "ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/phase3/data/{sample}/exome_alignment/{sample}.mapped.ILLUMINA.bwa.{pop}.exome.20120522.bam"

bamfh = open('data/samples.bams.txt', 'w')
for p in ('CEU', 'CHB+JPT', 'YRI'):
    pop = xl.parse(p, index_col=0)
    j = j.join(pop, how="inner")

    for s in pop.columns[1:]:
        if s in samples:
            bamfh.write("%s\t%s\n" % (s, samples[s]))
bamfh.close()


j.sort_values(by=['#chrom', 'start'], inplace=True)

j.to_csv('data/copy-numbers.hg18.wide.bed', index=False,
        float_format="%.0f", sep="\t", na_rep='nan')

jlong = pd.melt(j, id_vars=('#chrom', 'start', 'end'),
        value_vars=list(j.columns[4:]), var_name='sample', value_name='cn')

print jlong.shape
jlong = jlong.ix[jlong.cn != 2, :]
jlong.sort_values(by=['#chrom', 'start'], inplace=True)
print jlong.shape
print jlong.head()
jlong.to_csv('data/copy-numbers.hg18.long.bed', index=False,
        float_format="%.0f", sep="\t", na_rep='nan')

grouped = jlong.groupby(['#chrom','start', 'end', 'cn'], axis=0,
        as_index=False)
short = grouped.agg(lambda col: ",".join(col))
print short.__class__
short.sort_values(by=['#chrom', 'start', 'cn'], inplace=True)

short.to_csv('data/copy-numbers.hg18.samples.bed', index=False,
        float_format="%.0f", sep="\t", na_rep='nan')
