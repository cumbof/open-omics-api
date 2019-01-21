import json
from mongodb_driver import *
from flask import request, Response, session
from . import blueprint

@blueprint.route("/annotation/list")
def annotation_list():
    data = {
        'annotations': [
            {
                'annotation': 'geneexpression',
                'description': 'Gene Expression'
            },
            {
                'annotation': 'humanmethylation',
                'description': 'Human Methylation (platforms 27 and 450)'
            }
        ]
    }
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/annotation/<annotation_name>/all")
def annotation_all(annotation_name):
    mongodb_client = getClient()
    data = {
        'annotation': annotation_name,
        'data': get_documents(mongodb_client, annotation_name)
    }
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/annotation/<annotation_name>/coordinates")
def annotation_coordinates(annotation_name):
    mongodb_client = getClient()
    data = {
        'annotation': annotation_name,
        'coordinates': get_documents(mongodb_client, annotation_name, find_criteria={ 'chrom':1, 'start':1, 'end':1, 'strand':1 })
    }
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/annotation/<annotation_name>/ids")
def annotation_ids(annotation_name):
    mongodb_client = getClient()
    find_criteria = { }
    if annotation_name.lower() == "geneexpression":
        find_criteria = { 'ensembl_gene_id':1 }
    elif annotation_name.lower() == "humanmethylation":
        find_criteria = { 'composite_element_ref':1 }
    data = {
        'annotation': annotation_name,
        'ids': get_documents(mongodb_client, annotation_name, find_criteria=find_criteria)
    }
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/annotation/<annotation_name>/id/<elem_id>")
def annotation_id(annotation_name, elem_id):
    mongodb_client = getClient()
    find_attributes = { }
    if annotation_name.lower() == "geneexpression":
        find_attributes = { 'ensembl_gene_id': elem_id }
    elif annotation_name.lower() == "humanmethylation":
        find_attributes = { 'composite_element_ref': elem_id }
    data = {
        'annotation': annotation_name,
        'id': get_documents(mongodb_client, annotation_name, find_attributes=find_attributes)
    }
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;
