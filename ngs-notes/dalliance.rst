Dalliance Data Tutorial
=======================

`dalliance`_ is a web-based scrolling genome-browser. It can display data from
remote `DAS`_ servers or local or remote `BigWig`_ or `BigBed`_ files.
This will cover how to set up an html page that links to remote `DAS`_ services.
It will also show how to create and serve `BigWig`_ and `BigBed`_ files.

.. note::
    
    This document will be using hg18 for this tutorial, but it is applicable to
    any version available from your favorite database or `DAS`_ .


Creating A BigBed
=================

Getting a bed file from UCSC
----------------------------

  + From the `UCSC table browser`_ choose

    - genome: Human

    - assembly:  NCBI36/hg18

    - group: Genes and Gene Prediction Tracks

    - track: UCSC Genes

    - table: knownGene

    - output format "selected fileds from primary and related tables"

    - in text box, name it "knownGene.hg18.stuff.txt"

    - *click* "get output"

    - *check* kgXref under 'Linked Tables'

    - *click* 'Allow Selection From Checked Tables' at bottom of page.

    - *check* 'geneSymbol' from hg18.kgXref fields section

    - *click* 'get output' and a file named 'knownGene.hg18.stuff.txt' will be saved to your downloads directory. move it to your current directory.


  + To get this into bed format copy and paste this onto the command-line::

        grep -v '#' knownGene.hg18.stuff.txt | awk '
                    BEGIN { OFS = "\t"; FS="\t" } ;
                        {   split($7, astarts, /,/);
                            split($8, aends, /,/);
                            starts=""
                            sizes=""
                            exonCount=0
                            for(i=0; i < length(astarts); i++){
                                if (! astarts[i]) continue
                                sizes=sizes""(aends[i] - astarts[i])","
                                starts=starts""(astarts[i] = astarts[i] - $2)","
                                exonCount=exonCount + 1
                            }
                            print $1,$2,$3,$5","$4,1,$6,$2,$3,".",exonCount,sizes,starts
                        }' | sort -k1,1 -k2,2n > knownGene.hg18.bed


  + To create a `BigBed`_ from this, do (note if you're not on a 64 bit
    machine, you'll have to find the 32bit binaries::

        wget http://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64/fetchChromSizes
        wget http://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64/bedToBigBed
        chmod +x fetchChromSizes bedToBigBed
        ./fetchChromSizes hg18 > data/hg18.chrom.sizes
        ./bedToBigBed knownGene.hg18.bed data/hg18.chrom.sizes knownGene.hg18.bb

now knownGene.hg18.bb is a `BigBed`_ file containing both the UCSC and the common
name in the name column.

SQL
---

UCSC also has a public mysql server so the process of downloading to a bed can be simplified to::
    
    mysql --user=genome --host=genome-mysql.cse.ucsc.edu -A -D hg18 -P 3306   -e "select chrom,txStart,txEnd,K.name,X.geneSymbol,strand,exonStarts,exonEnds from knownGene as K,kgXref as X where  X.kgId=K.name;" > tmp.notbed
    grep -v txStart tmp.notbed | awk '
            BEGIN { OFS = "\t"; FS="\t" } ;
                {   
                    delete astarts;
                    delete aends;
                    split($7, astarts, /,/);
                    split($8, aends, /,/);
                    starts=""
                    sizes=""
                    exonCount=0
                    for(i=0; i < length(astarts); i++){
                        if (! astarts[i]) continue
                        sizes=sizes""(aends[i] - astarts[i])","
                        starts=starts""(astarts[i] = astarts[i] - $2)","
                        exonCount=exonCount + 1
                    }
                    print $1,$2,$3,$5","$4,1,$6,$2,$3,".",exonCount,sizes,starts
                }' | sort -k1,1 -k2,2n > knownGene.hg18.bed

then proceed as the last steps above to create the big bed file.

Displaying A BigBed in Dalliance
================================


From there, download dalliance::

    $ git://github.com/dasmoth/dalliance.git
    cd dalliance

and edit test.html, adding::


                {name: 'UCSC Genes',
                 bwgURI:               '/dalliance/knownGene.hg18.bb',
                },

before the line that looks like::


                {name: 'Repeats',

at around *line 55*.

Then edit your apache.conf (e.g. `/etc/apache2/sites-enabled/000-default`)
and put the following
(here i assume you cloned dalliance into `/usr/usr/local/src/dalliance-git`)::

    Alias /dalliance "/usr/local/src/dalliance-git"
    <Directory "/usr/locals/src/dalliance-git">

        Header set Access-Control-Allow-Origin "*"
        Header set Access-Control-Allow-Headers "Range"

        Options Indexes MultiViews FollowSymLinks
        AllowOverride None
        Order allow,deny
        Allow from all
    </Directory>

Then enable mod-headers apache module. On Ubuntu, that looks like::

    sudo a2enmod headers

Then point your browser to:: http://yourhost/dalliance/test.html
And you should see the your 'UCSC Genes' track in full glory along
with the other niceties of the `dalliance`_ browser.


.. _`dalliance`: http://www.biodalliance.org/
.. _`DAS`: http://dasregistry.org/
.. _`BigBed`: http://genome.ucsc.edu/goldenPath/help/bigBed.html
.. _`BigWig`: http://genome.ucsc.edu/goldenPath/help/bigWig.html
.. _`UCSC table browser`: http://genome.ucsc.edu/cgi-bin/hgTables

