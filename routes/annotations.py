import json
from flask import request, Response, session
from . import blueprint
from mongodb_driver import *

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
    js = json.dumps(data, indent=4, sort_keys=True)
    resp = Response(js, status=200, mimetype='application/json')
    return resp

@blueprint.route("/annotation/<annotation_name>/all")
def annotation_all(annotation_name):
    mongodb_client = getClient()
    data = {
        'annotation': 'annotation_' + annotation_name,
        'data': get_documents(mongodb_client, annotation_name)
    }
    js = json.dumps(data, indent=4, sort_keys=True)
    resp = Response(js, status=200, mimetype='application/json')
    return resp

@blueprint.route("/annotation/<annotation_name>/coordinates")
def annotation_coordinates(annotation_name):
    mongodb_client = getClient()
    data = {
        'annotation': 'annotation_' + annotation_name,
        'coordinates': get_documents(mongodb_client, annotation_name, find_criteria={ 'chrom':1, 'start':1, 'end':1, 'strand':1 })
    }
    js = json.dumps(data, indent=4, sort_keys=True)
    resp = Response(js, status=200, mimetype='application/json')
    return resp

@blueprint.route("/annotation/<annotation_name>/ids")
def annotation_ids(annotation_name):
    mongodb_client = getClient()
    find_criteria = { }
    id_annotation = ''
    ids_name = ''
    if annotation_name.lower() == "geneexpression":
        id_annotation = 'ensembl_gene_id'
        find_criteria = { id_annotation:1 }
        ids_name = 'ensembl_gene_ids'
    elif annotation_name.lower() == "humanmethylation":
        id_annotation = 'composite_element_ref'
        find_criteria = { id_annotation:1 }
        ids_name = 'composite_elements_ref'
    data = {
        'annotation': 'annotation_' + annotation_name,
        ids_name: get_documents(mongodb_client, annotation_name, find_criteria=find_criteria, get_one_element=id_annotation)
    }
    js = json.dumps(data, indent=4, sort_keys=True)
    resp = Response(js, status=200, mimetype='application/json')
    return resp

@blueprint.route("/annotation/<annotation_name>/id/<elem_id>")
def annotation_id(annotation_name, elem_id):
    mongodb_client = getClient()
    find_attributes = { }
    if annotation_name.lower() == "geneexpression":
        find_attributes = { 'ensembl_gene_id': elem_id }
    elif annotation_name.lower() == "humanmethylation":
        find_attributes = { 'composite_element_ref': elem_id }
    data = {
        'annotation': 'annotation_' + annotation_name,
        'id': get_documents(mongodb_client, annotation_name, find_attributes=find_attributes)
    }
    js = json.dumps(data, indent=4, sort_keys=True)
    resp = Response(js, status=200, mimetype='application/json')
    return resp

@blueprint.route("/annotation/<annotation_name>/overlap/chrom/<chrom>/start/<start>/end/<end>/strand/<strand>")
def annotation_overlap(annotation_name, chrom, start, end, strand):
    mongodb_client = getClient()
    find_attributes = {'chrom': chrom, 'start': {'$lte': int(end)}, 'end': {'$gte': int(start)}, 'strand': strand}
    data = {
        'annotation': 'annotation_' + annotation_name,
        'chrom': chrom,
        'start': start,
        'end': end,
        'strand': strand,
        'hits': get_documents(mongodb_client, 'annotation_' + annotation_name, find_attributes=find_attributes)
    }
    js = json.dumps(data, indent=4, sort_keys=True)
    resp = Response(js, status=200, mimetype='application/json')
    return resp
