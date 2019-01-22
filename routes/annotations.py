from flask import request, Response, session
from . import blueprint
import json
from mongodb_driver import *

@blueprint.route("/annotation/list")
def annotation_list():
    data = {
        'annotations': [
            {
                'annotation': 'annotation_geneexpression',
                'description': 'Gene Expression'
            },
            {
                'annotation': 'annotation_humanmethylation',
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
    id_annotation = ''
    ids_name = ''
    if annotation_name.lower() == "annotation_geneexpression":
        id_annotation = 'ensembl_gene_id'
        find_criteria = { id_annotation:1 }
        ids_name = 'ensembl_gene_ids'
    elif annotation_name.lower() == "annotation_humanmethylation":
        id_annotation = 'composite_element_ref'
        find_criteria = { id_annotation:1 }
        ids_name = 'composite_elements_ref'
    data = {
        'annotation': annotation_name,
        ids_name: get_documents(mongodb_client, annotation_name, find_criteria=find_criteria, get_one_element=id_annotation)
    }
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/annotation/<annotation_name>/id/<elem_id>")
def annotation_id(annotation_name, elem_id):
    mongodb_client = getClient()
    find_attributes = { }
    if annotation_name.lower() == "annotation_geneexpression":
        find_attributes = { 'ensembl_gene_id': elem_id }
    elif annotation_name.lower() == "annotation_humanmethylation":
        find_attributes = { 'composite_element_ref': elem_id }
    data = {
        'annotation': annotation_name,
        'id': get_documents(mongodb_client, annotation_name, find_attributes=find_attributes)
    }
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;
