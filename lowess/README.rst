Lowess
======

Lowess is locally weight polynomial regression.
This is a Cython wrapper to the implementation in `R <http://www.r-project-org/>`_
That implementation is GPL v2, so this is GPL as well.

Usage
=====

Usage is stolen from the `biopython <http://github.com/biopython/biopython>`_ docs for their lowess implementation.::

    >>> from lowess import lowess
    >>> import numpy as np
    >>> x = np.array([4,  4,  7,  7,  8,  9, 10, 10, 10, 11, 11, 12, 12, 12,
    ...               12, 13, 13, 13, 13, 14, 14, 14, 14, 15, 15, 15, 16, 16,
    ...               17, 17, 17, 18, 18, 18, 18, 19, 19, 19, 20, 20, 20, 20,
    ...                20, 22, 23, 24, 24, 24, 24, 25], np.float)
    >>> y = np.array([2, 10,  4, 22, 16, 10, 18, 26, 34, 17, 28, 14, 20, 24,
    ...               2800, 26, 34, 34, 46, 26, 36, 60, 80, 20, 26, 54, 32, 40,
    ...               32, 40, 50, 42, 56, 76, 84, 36, 46, 68, 32, 48, 52, 56,
    ...               64, 66, 54, 70, 92, 93, 120, 85], np.float)

    >>> result = lowess(x, y)
    >>> print "%.3f ... %.3f" % (result[0], result[-1])
    4.712 ... 85.470

On large datasets, this runs *much* faster and uses less memory than the 
biopython implementation.
