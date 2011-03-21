

manhattan-plot.py
=================

Generate a manhattan plot given a file with (at least)
chromosome, x, p-value.
Offers a number of command-line options and the code is simple
enough that it can be further customized.

Usage::

    manhattan-plot.py [options] files

    plot a manhattan plot of the input file(s).


    Options:
      -h, --help       show this help message and exit
      --no-log         don't do -log10(p) on the value
      --cols=COLS      zero-based column indexes to get chr, position, p-value
                       respectively e.g. 0,1,2
      --colors=COLORS  cycle through these colors
      --image=IMAGE    save the image to this file. e.g. manhattan.png
      --title=TITLE    title for the image.
      --sep=SEP        data separator, default is [tab]
      --lines          plot the p-values as lines extending from the x-axis rather
                       than points in space


a command like::

    $ python manhattan-plot.py --cols 0,1,6 input.bed

generates

.. image:: https://github.com/brentp/bio-playground/raw/master/plots/images/manhattan.png

there are a number of options, including adding custom colors.

    $ python manhattan-plot.py --cols 0,1,6 input.bed

generates

.. image:: https://github.com/brentp/bio-playground/raw/master/plots/images/manhattan.rgbk.png

