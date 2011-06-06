import socket
import os.path as op
import os

class IGV(object):
    r"""
    Simple wrapper to the IGV (http://www.broadinstitute.org/software/igv/home)
    socket interface (http://www.broadinstitute.org/software/igv/PortCommands)

    requires:

        1) you have IGV running on your machine (launch with webstart here:
                http://www.broadinstitute.org/software/igv/download)

        2) you have enabled port communication in
                View -> Preferences... -> Advanced

    example usage:

        >>> igv = IGV()
        >>> igv.genome('hg19')
        12

        #>>> igv.load('http://www.broadinstitute.org/igvdata/1KG/pilot2Bams/NA12878.SLX.bam')
        #74
        >>> igv.go('chr1:45,600-45,800')
        24

    #save as svg, png, or jpg
        >>> igv.save('/tmp/r/region.svg')
        >>> igv.save('/tmp/r/region.png')

    # go to a gene name.
        >>> igv.go('muc5b')
        11
        >>> igv.save('muc5b.png')

    # get a list of commands that will work as an IGV batch script.
        >>> print "\n".join(igv.commands)
        snapshotDirectory /tmp/igv
        genome hg19
        goto chr1:45,600-45,800
        snapshotDirectory /tmp/r
        snapshot region.svg
        snapshot region.png
        goto muc5b
        snapshot muc5b.png

    Note, this example will finish and there will be some delay before the
    images appear as the BAM file is quite large.

    """
    _socket = None
    _path = None
    def __init__(self, host='127.0.0.1', port=60151, snapshot_dir='/tmp/igv'):
        self.host = host
        self.port = port
        self.commands = []
        self.connect()
        self.set_path(snapshot_dir)

    def connect(self):
        if self._socket: self._socket.close()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self.host, self.port))

    def go(self, position):
        return self.send('goto ' + position)
    goto = go

    def genome(self, name):
        return self.send('genome ' + name)

    def load(self, url):
        return self.send('load ' + url)


    def set_path(self, snapshot_dir):
        if snapshot_dir == self._path: return
        if not op.exists(snapshot_dir):
            os.makedirs(snapshot_dir)

        self.send('snapshotDirectory %s' % snapshot_dir)
        self._path = snapshot_dir

    def send(self, cmd):
        self.commands.append(cmd)
        return self._socket.send(cmd + '\n')

    def save(self, path=None):
        if path is not None:
            # igv assumes the path is just a single filename, but
            # we can set the snapshot dir. then just use the filename.
            dirname = op.dirname(path)
            if dirname:
                self.set_path(dirname)
            self.send('snapshot ' + op.basename(path))
        else:
            self.send('snapshot')
    snapshot = save

if __name__ == "__main__":
    import doctest
    doctest.testmod()

