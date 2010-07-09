given:

    * a set of motifs and a count of their occurence in a genome or region (motif_counts.txt)
    * a set of patterns/groups of motifs and their occurrence in the genome

return a p-value for each pattern. where a low p-value indicates that it is rare to see that pattern
by chance given the frequency of occurence of its constituent motifs.

the count of motif patterns is used only to estimate the lengths of observed patterns (presumably in a
single genespace).

useage::

    python motif_significance.py -m motif_counts.txt -p patterns.txt -n 2000000

where -n is the number of monte-carlo simulations to run in order to determine significance.

