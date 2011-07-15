.. contents::

Miscellaneous scripts for bioinformatics that dont merit their own repo.
All under MIT License unless otherwise specified.

Ks Calc
--------
Abnormal nucleotide frequency tends to throw off normal procedures for estimating `evolutionary models <http://en.wikipedia.org/wiki/Models_of_DNA_evolution>`_. A practical situation is when calculating the Ks values for the grass genes where a significant portion of them are high-GC genes (see details `here <http://tanghaibao.blogspot.com/2009/08/high-gc-grass-genes.html>`_). In the case of high GC genes, most of the substitutions will be either G or C, therefore the Jukes-Cantor correction will under-estimate the Ks values. The codon models in PAML, on the contrary, tend to over-estimate Ks values. The Ks calculator we want to implement here, ignores the inference of models (where it is difficult anyway, since you have very few sites to estimate the parameters in the model). Instead, we ask this: **given biased substitutions, lengths, run simulations and try to fit an evolutionary model based on the simulations.**

.. image:: http://chart.apis.google.com/chart?cht=lc&chls=8|8&chd=t2:65,65,65|75,75,75|40,50,80&chs=300x200&chm=V,FFFFFF,0,,25|@tObserved+alignment,,0,.05:.87,10|@twith+difference+D,,0,.05:.8,10|@tSimulate+alignments,,0,.55:.87,10|@twith+various+Ks,,0,.55:.8,10|@tProb(D)=0.3,,0,.3:.45,10|@tProb(D)=0.6,ff0000,0,.3:.37,10|@tProb(D)=0.4,,0,.3:.3,10|@tKs=0.1,,0,.15:.45,10|@tKs=0.2,ff0000,0,.15:.37,10|@tKs=0.3,,0,.15:.3,10|@tKs=...,808080,0,.15:.23,10|@tMaximum+Likelihood+Estimate,ff0000,0,.5:.37,10|a,990066,2,1,9.0&chma=0,0,30,0
    :alt: method


