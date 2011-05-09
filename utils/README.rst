

join
====

Usage::
        join.py [options] filea:col# fileb:col#

        join filea with fileb by looking for the same value in col#

        col numbers are 0-based indexing.

        can never get linux join to work as i want. also handles files with different
        seperators.


        Options:
          -h, --help   show this help message and exit
          --sepa=SEPA  separator for 1st file
          --sepb=SEPB  separator for 2nd file
          -x           only print the shared column once.

gene-list overlap
=================

Uses the hypergeometric distribtion to calculate the probality of gene-list
overlap.
Given 2 lists (or gene sets) we know they came from, e.g. `GG` genes
and we know there are `AA` genes in list-A and `BB` genes in list-B. What is the
probability that they share `SS` genes? ::

    $ ./list_overlap_p.py SS GG AA BB

e.g.::

    $ ./list_overlap_p.py 10 30000 345 322
    0.0043679470685

gives the probability that 10 genes are shared in 2 random lists of length 345 and
322 given that those lists are drawn from a set of 30K genes.
