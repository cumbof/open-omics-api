from flask import Response, redirect
from . import blueprint

import json, yaml

# load config
config = None;
with open("./config.yaml", 'r') as cfg:
    config = yaml.load(cfg);

app_name = str(config["app"]["name"]);
app_version = str(config["app"]["version"]);

@blueprint.route("/routes")
def routes():
    data = {
        'application': app_name,
        'release': app_version,
        'routes': {
            'api': [
                '/api/routes',
                '/api/documentation',
                '/api/version'
            ],
            'annotation': [
                '/annotation/list',
                '/annotation/<annotation_name>/all',
                '/annotation/<annotation_name>/coordinates',
                '/annotation/<annotation_name>/ids',
                '/annotation/<annotation_name>/id/<elem_id>'
            ],
            'experiment': [
                '/experiment/sources', 
                '/experiment/datatypes', 
                '/experiment/tumors', 
                '/experiment/programs',
                '/experiment/source/<source>/programs',
                '/experiment/source/<source>/aliquots',
                '/experiment/source/<source>/datatypes',
                '/experiment/source/<source>/tumors',
                '/experiment/source/<source>/program/<program>/aliquots',
                '/experiment/source/<source>/program/<program>/datatypes',
                '/experiment/source/<source>/program/<program>/tumors',
                '/experiment/source/<source>/program/<program>/tumor/<tumor>/datatypes',
                '/experiment/source/<source>/program/<program>/tumor/<tumor>/aliquots',
                '/experiment/source/<source>/program/<program>/tumor/<tumor>/datatype/<datatype>/aliquots',
                '/experiment/source/<source>/program/<program>/tumor/<tumor>/datatype/<datatype>/aliquot/<aliquot>/all',
                '/experiment/source/<source>/program/<program>/tumor/<tumor>/datatype/<datatype>/aliquot/<aliquot>/coordinates',
                '/experiment/source/<source>/program/<program>/tumor/<tumor>/datatype/<datatype>/aliquot/<aliquot>/ids',
                '/experiment/source/<source>/program/<program>/tumor/<tumor>/datatype/<datatype>/aliquot/<aliquot>/id/<elem_id>/all',
                '/experiment/aliquot/<aliquot>/list'
            ],
            'metadata': [
                '/metadata/sources',
                '/metadata/source/<source>/attribute/<attribute>/all',
                '/metadata/source/<source>/attribute/<attribute>/value/<value>/aliquots',
                '/metadata/attribute/<attribute>/all',
                '/metadata/attribute/<attribute>/value/<value>/aliquots',
                '/metadata/aliquot/<aliquot>/list'
            ]
        }
    };
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/api/documentation")
def documentation():
    return redirect("https://opengenomics.docs.apiary.io/", code=302);

@blueprint.route("/api/version")
def api_version():
    data = {
        'version': app_version
    }
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/api/sources")
def api_sources():
    data = {
        'sources': [
            'Genomic Data Commons (GDC)'
        ]
    }
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;
