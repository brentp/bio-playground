import numpy as np
cimport numpy as np
import cython

cdef extern from "_lowess.c":

    void clowess(double *x, double *y, int n,
         double f, int nsteps, double delta,
         double *ys, double *rw, double *res)


#@cython.embedsignature(True)
def lowess(np.ndarray[np.double_t, cast=True, ndim=1] x,
           np.ndarray[np.double_t, cast=True, ndim=1] y,
           double f=2/3., int iters=3):
    """
        lowess(xs, ys, f=2/3., iters=3)
    perform lowess smoothing given numpy arrays for x and y
    of the same shape.

    `f` gives the proportion of points in the plot which influence each value.
        larger values give more smooth results.
    `iter` the number of smoothing iterations to perform.

    this function calls the C-code from the R stats lowess implementation.
    """

    cdef np.ndarray[np.double_t, cast=True, ndim=1] ys = np.empty(x.shape[0])
    cdef np.ndarray[np.double_t, cast=True, ndim=1] rw = np.empty(x.shape[0])
    cdef np.ndarray[np.double_t, cast=True, ndim=1] res = np.empty(x.shape[0])

    cdef double delta = 0.01 * (x.max() - x.min())

    clowess(<double *>x.data, <double *>y.data, <int>x.shape[0], f, iters, delta,
                <double *>ys.data,
                <double *>rw.data,
                <double *>res.data)
    return ys

def test():
    from Bio.Statistics.lowess import lowess as bio_lowess

    import numpy as np

    x = np.array([4,  4,  7,  7,  8,  9, 10, 10, 10, 11, 11, 12, 12, 12,
                         12, 13, 13, 13, 13, 14, 14, 14, 14, 15, 15, 15, 16, 16,
                         17, 17, 17, 18, 18, 18, 18, 19, 19, 19, 20, 20, 20, 20,
                         20, 22, 23, 24, 24, 24, 24, 25], np.float)

    y = np.array([2, 10,  4, 22, 16, 10, 18, 26, 34, 17, 28, 14, 20, 24,
                         2800, 26, 34, 34, 46, 26, 36, 60, 80, 20, 26, 54, 32, 40,
                         32, 40, 50, 42, 56, 76, 84, 36, 46, 68, 32, 48, 52, 56,
                         64, 66, 54, 70, 92, 93, 120, 85], np.float)

    x = x.repeat(40)
    y = y.repeat(40)
    import time
    t = time.time()
    bio_result = bio_lowess(x, y)
    print "Bio:%.2f" % (time.time() - t)
    t = time.time()
    r_result = lowess(x, y)
    print "RCy:%.2f" % (time.time() - t)

    for result in (bio_result, r_result):
        print "[%0.2f, ..., %0.2f]" % (result[0], result[-1])

    diff = np.abs(bio_result - r_result)
    print diff.max()
    print diff.mean()
