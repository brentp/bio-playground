#!/usr/bin/env python
"""

    %prog [options] train-file [test-file]


NOTE: this expects svm-train and svm-predict to be on your path. so you may call with:

    PATH=/dir/containing/libsvm:$PATH %prog ...
"""


import sys
import os.path as op
import numpy as np
import random
from subprocess import Popen, PIPE
from multiprocessing import cpu_count

import optparse

def check_path():
    """
    make sure the libsvm stuff is on the path
    """
    import os
    paths = (op.abspath(p) for p in os.environ['PATH'].split(":"))
    for p in paths:
        if op.exists(op.join(p, "svm-train")): return True
    for path in ("../", "./"):
        if op.exists(path + "svm-train"):
            os.environ['PATH'] += ":" + path
            return True

    print >>sys.stderr, "\n** svm-train not found in path **\n" + ("*" * 80)

    return False

def scale(test_dataset, train_dataset, out_prefix):
    cmd_tmpl = 'svm-train -c %(c)f -g %(g)f -v %(fold)i %(extra_params)s %(train_dataset)s'

    range_file = out_prefix + ".range"
    scaled_train = train_dataset + ".scale"

    cmd = 'svm-scale -s "%(range_file)s" "%(train_dataset)s" > "%(scaled_train)s"' % locals()
    p = Popen(cmd, shell=True, stdout=PIPE)
    p.wait()
    assert p.returncode == 0, (p.stdout.read())

    # scale the test file according to range in train file.
    scaled_test = test_dataset + ".scale"
    cmd = 'svm-scale -r "%(range_file)s" "%(test_dataset)s" > "%(scaled_test)s"' % locals()
    p = Popen(cmd, shell=True, stdout=PIPE)
    p.wait()
    assert p.returncode == 0, (p.stdout.read())
    return scaled_train, scaled_test

def main():
    p = optparse.OptionParser(__doc__)
    p.add_option("--c-range", dest="c_range", default="-7:17:2",
            help="log2 range of values in format start:stop:step")
    p.add_option("--g-range", dest="g_range", default="-18:7:2",
            help="log2 range of g values in format start:stop:step")
    p.add_option("--n-threads", dest="n_threads", default=cpu_count(), type='int',
            help="number of threads to use")
    p.add_option("--out-prefix", dest="out_prefix",
            help="where to send results")
    p.add_option("--x-fold", dest="x_fold", type="int", default=5,
            help="number for cross-fold validation on training set")
    p.add_option("--scale", dest="scale", action="store_true", default=False,
            help="if specified, perform scaling (svm-scale) on the dataset(s)")

    opts, args = p.parse_args()
    if len(args) < 1 or not check_path(): sys.exit(p.print_help())

    train_dataset = op.abspath(args[0])
    assert op.exists(train_dataset)

    test_dataset = op.abspath(args[1]) if len(args) > 1 else None
    if test_dataset: assert op.exists(test_dataset)

    c_range = np.arange(*map(float, opts.c_range.split(":")))
    g_range = np.arange(*map(float, opts.g_range.split(":")))

    out_prefix = opts.out_prefix if opts.out_prefix else op.splitext(train_dataset)[0]
    # set parameters
    param_list = list(gen_params(c_range, g_range))
    print >>sys.stderr, "running %i parameter groups across a grid in batches of %i" \
                    % (len(param_list), opts.n_threads)

    if opts.scale:
        print >>sys.stderr, "Scaling datasets"
        train_dataset, test_dataset = scale(train_dataset, test_dataset, out_prefix)

    fold = opts.x_fold
    extra_params = ""
    results = {}
    cmd_tmpl = 'svm-train -c %(c)f -g %(g)f -v %(fold)i %(extra_params)s %(train_dataset)s'

    while param_list:
        procs = []
        for i in range(opts.n_threads):
            if not param_list: break
            c, g = param_list.pop()
            run_cmd = cmd_tmpl % locals()
            procs.append((run_cmd, c, g, Popen(run_cmd, shell=True, stdout=PIPE)))
        for cmd, c, g, p in procs:
            p.wait()
            for line in p.stdout:
                if not "Cross" in line: continue
                validation = float(line.split()[-1][0:-1])
                if results and validation > max(results.keys()): line = line.strip() + " *BEST*\n"
                results[validation] = (c, g)

                #print >>sys.stderr, "ran: %s\n%s" % (cmd, line)

    # grab the best one.
    valid_pct, (c, g) = sorted(results.items())[-1]
    print "Best Cross Validation Accuracy: %.2f with parameters c:%s,  g:%s" %\
            (valid_pct, c, g)
    if test_dataset is None: return True

    cmd_tmpl = 'svm-train -c %(c)f -g %(g)f %(extra_params)s %(train_dataset)s %(model_file)s'
    model_file = out_prefix + ".model"
    print "Saving model file to %s" % model_file

    # run once more and save the .model file for the best scoring params.
    Popen(cmd_tmpl % locals(), shell=True, stdout=PIPE).wait()


    # now run the test dataset through svm-predict with best parameters
    #./svm-predict -b 0 /tmp/charm.svm.test /tmp/charm.svm.model /tmp/out.predict
    cmd_tmpl = "svm-predict %(test_dataset)s %(model_file)s %(out_prefix)s.predict"
    p = Popen(cmd_tmpl % locals(), shell=True, stdout=PIPE)
    print p.stdout.read().strip()


def gen_params(c_range, g_range):
    random.shuffle(c_range)
    random.shuffle(g_range)
    nr_c = float(len(c_range))
    nr_g = float(len(g_range))
    i, j = 0, 0
    while i < nr_c or j < nr_g:
        if i/nr_c < j/nr_g:
            # increase C resolution
            for k in range(j):
                yield((2**c_range[i], 2**g_range[k]))
            i = i + 1
        else:
            # increase g resolution
            for k in range(i):
                yield((2**c_range[k], 2**g_range[j]))
            j = j + 1

if __name__ == "__main__":
    main()
