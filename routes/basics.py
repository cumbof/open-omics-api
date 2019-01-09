from flask import Response, redirect
from . import blueprint

import json, yaml

# load config
config = None;
with open("./config.yaml", 'r') as cfg:
    config = yaml.load(cfg);

app_name = str(config.get("app", "name"));
app_version = str(config.get("app", "version"));

@blueprint.route("/routes")
def routes():
    data = {
        'application': app_name,
        'release': app_version,
        'routes': {
            'api': [
                '/api/documentation',
                '/api/version'
            ],
            'sources': '/sources',
            'tree': [
                '/tree', 
                #'/tree/<tree_id>', 
                '/tree/<tree_id>/accession', 
                '/tree/<tree_id>/accession/<accession_number>', 
                '/tree/<tree_id>/query',
                '/status/<query_id>'
            ]
        }
    };
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/api/documentation")
def documentation():
    return redirect("https://btman.docs.apiary.io/", code=302);

@blueprint.route("/api/version")
def api_version():
    data = {
        'version': app_version
    }
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;
