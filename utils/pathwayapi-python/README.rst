pathwayapi
==========

A python interface to http://www.pathwayapi.com/


in addition the the module, it can be called from the command-line
like::

    $ python pathwayapi.py some.input 7

where some.input has gene names in the 8th (starting from 0) column.
The result, sent to stdout, will be the same as the input but with an additional,
final column with pathway information. if that information is not available
for the given gene name, the column is empty.
