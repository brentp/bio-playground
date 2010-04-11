FileIndex
=========

index flat files. see: `blogpost <http://hackmap.blogspot.com/2010/04/fileindex.html>`_
example::

    >>> FileIndex.create(f, lambda fh: SamLine(fh).name, allow_multiple=True)
    >>> fi = FileIndex(f, SamLine, allow_multiple=True)
    >>> [(s.name, s.ref_seqid, s.ref_loc) for s in fi['23351265']]
    [('23351265', '2', 8524), ('23351265', '3', 14202495)]

