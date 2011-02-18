libsvm-grid.py
==============

`libsvm-grid.py` is a script to replace the easy.py and grid.py distributed
with `libsvm`_. It's usage looks like::

    $ python libsvm-grid.py 
    Usage: 

        libsvm-grid.py [options] train-file [test-file]

    Options:
      -h, --help            show this help message and exit
      --c-range=C_RANGE     log2 range of values in format start:stop:step
      --g-range=G_RANGE     log2 range of g values in format start:stop:step
      --n-threads=N_THREADS
                            number of threads to use
      --out-prefix=OUT_PREFIX
                            where to send results
      --x-fold=X_FOLD       number for cross-fold validation on training set
      --scale               if specified, perform scaling (svm-scale) on the
                            dataset(s)


It expects `svm-train`, `svm-predict`, and `svm-scale` to be on the path
so it may be called like::

    $ PATH=/usr/local/src/libsvm-3.0/:$PATH python libsvm-grid.py --scale --n-threads 8 some.train-data some.test-data

This will scale the train and test data, run `svm-train` in 8 parallel processes (not actually threads) on the scaled train data for a grid of parameter values. It will take the parameters with the highest cross-validation accuracy and run them on the scaled test data.


TODO
----

Output file for AUC/ROC-curve


.. _`libsvm`: http://www.csie.ntu.edu.tw/~cjlin/libsvm/

