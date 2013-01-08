import socket
import os.path as op
import os
import sys

class IGV(object):
    r"""
    Simple wrapper to the IGV (http://www.broadinstitute.org/software/igv/home)
    socket interface (http://www.broadinstitute.org/software/igv/PortCommands)

    requires:

        1) you have IGV running on your machine (launch with webstart here:
                http://www.broadinstitute.org/software/igv/download)

        2) you have enabled port communication in
                View -> Preferences... -> Advanced

    Successful commands return 'OK'

    example usage:

        >>> igv = IGV()
        >>> igv.genome('hg19')
        'OK'

        #>>> igv.load('http://www.broadinstitute.org/igvdata/1KG/pilot2Bams/NA12878.SLX.bam')
        'OK'
        >>> igv.go('chr1:45,600-45,800')
        'OK'

    #save as svg, png, or jpg
        >>> igv.save('/tmp/r/region.svg')
        'OK'
        >>> igv.save('/tmp/r/region.png')
        'OK'

    # go to a gene name.
        >>> igv.go('muc5b')
        'OK'
        >>> igv.sort()
        'OK'
        >>> igv.save('muc5b.png')
        'OK'

    # get a list of commands that will work as an IGV batch script.
        >>> print "\n".join(igv.commands)
        snapshotDirectory /tmp/igv
        genome hg19
        goto chr1:45,600-45,800
        snapshotDirectory /tmp/r
        snapshot region.svg
        snapshot region.png
        goto muc5b
        sort base
        snapshot muc5b.png

    Note, there will be some delay as the browser has to load the annotations
    at each step.

    """
    _socket = None
    _path = None
    def __init__(self, host='127.0.0.1', port=60151, snapshot_dir='/tmp/igv'):
        self.host = host
        self.port = port
        self.commands = []
        self.connect()
        self.set_path(snapshot_dir)

    @classmethod
    def start(cls, jnlp="igv.jnlp", url="http://www.broadinstitute.org/igv/projects/current/"):
        import subprocess
        from threading import Thread
        import time

        def readit(ffrom, fto, wait):
            for line in iter(ffrom.readline, b''):
                if "Listening on port" in line:
                    wait[0] = False
                fto.write(line + '\n')
            ffrom.close()

        p = subprocess.Popen("/usr/bin/javaws -Xnosplash %s%s" % (url, jnlp),
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        wait = [True]
        _tout = Thread(target=readit, args=(p.stdout, sys.stdout, wait))
        _terr = Thread(target=readit, args=(p.stderr, sys.stderr, wait))
        _tout.daemon = _terr.deamon = True
        _tout.start()
        _terr.start()
        while p.poll() is None and wait[0]:
            time.sleep(10)
            print "waiting", wait


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

    def sort(self, option='base'):
        """
        options is one of: base, position, strand, quality, sample, and
        readGroup.
        """
        assert option in ("base", "position", "strand", "quality", "sample",
                         "readGroup")
        return self.send('sort ' + option)


    def set_path(self, snapshot_dir):
        if snapshot_dir == self._path: return
        if not op.exists(snapshot_dir):
            os.makedirs(snapshot_dir)

        self.send('snapshotDirectory %s' % snapshot_dir)
        self._path = snapshot_dir

    def expand(self, track):
        self.send('expand %s' % track)

    def collapse(self, track):
        self.send('collapse %s' % track)

    def clear(self):
        self.send('clear')

    def send(self, cmd):
        self.commands.append(cmd)
        self._socket.send(cmd + '\n')
        return self._socket.recv(10).rstrip('\n')

    def save(self, path=None):
        if path is not None:
            # igv assumes the path is just a single filename, but
            # we can set the snapshot dir. then just use the filename.
            dirname = op.dirname(path)
            if dirname:
                self.set_path(dirname)
            return self.send('snapshot ' + op.basename(path))
        else:
            return self.send('snapshot')
    snapshot = save

if __name__ == "__main__":
    import doctest
    doctest.testmod()

