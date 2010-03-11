#!/usr/bin/python


from flatfeature import Bed
import simplejson
import sys
import os.path as op
sys.path = [op.dirname(__file__)] + sys.path
from bottle import route, request, response, default_app

bed = Bed('/opt/src/flatfeature/data/brachy_v1.bed', '/home/brentp/work/bio-me/flank/data/rice_v5_brachy_v1/brachy_v1.fasta')


@route('/', method='POST')
def index():
    action = request.POST.get('action')
    response.headers['Content-Type'] = 'text/plain'
    if action == 'lookup':
        q = request.POST.get('query')
        return q

    elif action == 'range':
        l = int(request.POST.get('left'))
        r = int(request.POST.get('right'))
        seqid = request.POST.get('assembly')
        feats = bed.get_features_in_region(seqid, l, r)
        data = []

        for feat in feats:
            parent = feat['accn']
            s = int(feat['start'])
            row = [None, feat['accn'], feat['strand'], "mRNA", s, int(feat['end']) - s]
            data.append(row)
            for i, (start, end) in enumerate(feat['locs']):
                row = [parent, str(i), feat['strand'], "CDS", start, end - start]
                data.append(row)

        j = {'success': True, 'data': data, 'l': l, 'r': r}
        response.headers['Content-Type'] = 'text/javascript'
        return simplejson.dumps(j)

@route('/', method='GET')
@route('/genome')
def genome():
    response.headers['Content-Type'] = 'text/plain'
    chrs = [{"id": seqid, "size": len(bed.fasta[seqid])} for seqid in bed.fasta.keys()]
    d = {'success': True, 'data': {'institution': {'name': "UCB", "url": 'http://arabidopsis.org'},
        "service": {"title": "Brachypodium distachyon", "version": 1}, "genome": {"assemblies": chrs }}}
    return simplejson.dumps(d)

application = default_app()
