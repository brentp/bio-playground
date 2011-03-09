

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
