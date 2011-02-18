libsvm-grid.py
==============

`libsvm-grid.py` is a script to replace the easy.py and grid.py distributed
with `libsvm`_. It's usage looks like::

    $ python libsvm-grid.py 
    Options:
      -h, --help            show this help message and exit
      --kernel=KERNEL       one of linear/polynomial/rbf/sigmoid
      --c-range=C_RANGE     log2 range of values in format start:stop:step
                            [-7:12:2]
      --g-range=G_RANGE     log2 range of g values in format start:stop:step
                            [-15:7:2]
      --n-threads=N_THREADS
                            number of threads to use [4]
      --out-prefix=OUT_PREFIX
                            where to send results
      --x-fold=X_FOLD       number for cross-fold validation on training set [8]
      --scale               if specified, perform scaling (svm-scale) on the
                            dataset(s) before calling svm-train. [False]
      --split=SPLIT         if specified split the training file into 2 files. one
                            for testing and one for training. --split 0.8 would
                            use 80% of the lines for training. the selection is
                            random. this is used instead of specifying a training
                            file.


It expects `svm-train`, `svm-predict`, and `svm-scale` to be on the path
so it may be called like::

    $ PATH=/usr/local/src/libsvm-3.0/:$PATH python libsvm-grid.py --scale --n-threads 8 some.train-data some.test-data

This will scale the train and test data, run `svm-train` in 8 parallel processes (not actually threads) on the scaled train data for a grid of parameter values. It will take the parameters with the highest cross-validation accuracy and run them on the scaled test data.

`libsvm-grid.py` will automatically guess the number of processors available on
the calling machine and use that many if `--n-threads` is not specified.

The output will be something like::

    Best Cross Validation Accuracy: 66.67 with parameters c:0.125,  g:4.0

In addition to the files some.train-data.scale and some-test-data.scale and some-test-data.model if a test set is specified.


TODO
----

Output file for AUC/ROC-curve


.. _`libsvm`: http://www.csie.ntu.edu.tw/~cjlin/libsvm/

