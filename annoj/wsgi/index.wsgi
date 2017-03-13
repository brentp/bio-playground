#!/usr/bin/python
import sys
import os.path as op
PATH = op.dirname(__file__)
sys.path = [PATH] + sys.path
from bottle import route, request, response, default_app
from mako.template import Template
from mako.lookup import TemplateLookup
tmpl = op.join(op.dirname(PATH), "templates")

@route("/:organism")
def index(organism):
    t = Template(filename=op.join(tmpl, "index.mako"), lookup=TemplateLookup(directories=tmpl))
    return t.render(organism=organism, seqid='Bd1', position=1234)


application = default_app()

