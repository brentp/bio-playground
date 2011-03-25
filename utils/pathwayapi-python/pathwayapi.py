import simplejson
import urllib
import anydbm
import sys
import gzip

def nopen(f, mode="r"):
    return sys.stdin if f == "-" \
         else gzip.open(f, mode) if f.endswith(".gz") else open(f, mode)

__all__ = ['api']

def get(url, cache=anydbm.open('t.cache', 'c')):
    if url in cache:
        json = cache[url]
    else:
        json = urllib.urlopen(url).read()
        cache[url] = json
        cache.sync()
    return simplejson.loads(json)

class api(object):
    methods = {
        'GetGeneID': ('gene_name', ('gene_name', 'gene_id'))
        }
    url = 'http://www.pathwayapi.com/api/API_%s.php?%s='


    def get_gene_ids(self, *gene_names):
        """
        >>> a = api()
        >>> a.get_gene_ids('GATA3')
        {'GATA3': '2625'}
        """
        url = self.url % ("GetGeneID", "SearchGene")
        names = {}
        import sys
        for gene_name in gene_names:
            arr = get(url + gene_name)
            for row in arr:
                # TODO: handle multiples.
                names[row[0]] = row[1]
        return names

    def get_pathways(self, *gene_names):
        """
        >>> a = api()
        >>> a.get_pathways('GATA3')
        {'GATA3': ['Adipogenesis']}
        """
        url = self.url % ("GetGenePathways", "SearchGene")

        gene_names = gene_names
        if not isinstance(gene_names, dict):
            gene_names = self.get_gene_ids(*gene_names)
        pathways = {}
        for gene_name, gene_id in gene_names.iteritems():
            if gene_id == []:
                pathways[gene_name] = []
                continue

            pw = get(url + gene_id)
            if pw != []: pw = pw.values() # ids are just numbers
            pathways[gene_name] = pw
        return pathways



def main(fname, col):
    a = api()

    for line in nopen(fname):
        line = line.rstrip("\r\n")
        if line[0] == "#":
            print line + "\tpathways"
            continue
        toks = line.split("\t")
        # they might just have a gene list.
        name = toks[1] if len(toks) == 1 else toks[col]
        p = a.get_pathways(name)
        values = [x for x in p.values() if x !=[]]
        try:
            print line + "\t" + ",".join(values[0] if values and values[0] else [])
        except:
            print values
            raise

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    if len(sys.argv) > 1:
        # assume it's a bed and get the name from the 4th col unless it's specified.
        main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 3)

