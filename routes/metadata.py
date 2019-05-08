import json
from mongodb_driver import *
from flask import request, Response, session
from . import blueprint

@blueprint.route("/metadata/sources")
def metadata_sources():
    data = {
        'sources': [
            {
                'id': 'gdc',
                'description': 'Genomic Data Commons (GDC)'
            }
        ]
    }
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/metadata/source/<source>/attribute/<attribute>/all")
def metadata_source_attribute_all(source, attribute):
    mongodb_client = getClient()
    values = get_documents(mongodb_client, "metadata", find_attributes={ 'source': source }, find_criteria={ attribute:1 })
    parsed_values = set()
    for val in values:
        if attribute in val:
            parsed_values.add( val[attribute] )
    data = {
        'source': source,
        'attribute': attribute,
        'values': list(parsed_values)
    }
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/metadata/source/<source>/attribute/<attribute>/value/<value>/urls") 
def metadata_source_attribute_value(source, attribute, value):
    mongodb_client = getClient()
    values = get_documents(mongodb_client, "metadata", find_attributes={ 'source': source, attribute: value }, find_criteria={ 'gdc__program__name':1, 'gdc__project__project_id':1, 'gdc__type':1, 'gdc__aliquots__aliquot_id':1 })
    hits = [ ]
    for val in values:
        if 'gdc__program__name' in val and 'gdc__project__project_id' in val and 'gdc__type' in val and 'gdc__aliquots__aliquot_id' in val:
            hits.append( "/experiment/source/"+source+"/program/"+val["gdc__program__name"]+"/tumor/"+val["gdc__project__project_id"]+"/datatype/"+val["gdc__type"]+"/aliquot/"+val["gdc__aliquots__aliquot_id"]+"/all" )
    data = {
        'source': source,
        'attribute': attribute,
        'value': value,
        'hits': hits
    }
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/metadata/attribute/<attribute>/all")
def metadata_attribute_all(attribute):
    mongodb_client = getClient()
    values = get_documents(mongodb_client, "metadata", find_criteria={ attribute:1 })
    parsed_values = set()
    for val in values:
        if attribute in val:
            parsed_values.add( val[attribute] )
    data = {
        'attribute': attribute,
        'values': list(parsed_values)
    }
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/metadata/attribute/<attribute>/value/<value>/urls")
def metadata_attribute_value(attribute, value):
    mongodb_client = getClient()
    values = get_documents(mongodb_client, "metadata", find_attributes={ attribute: value }, find_criteria={ 'source':1, 'gdc__program__name':1, 'gdc__project__project_id':1, 'gdc__type':1, 'gdc__aliquots__aliquot_id':1 })
    hits = [ ]
    for val in values:
        if 'source' in val and 'gdc__program__name' in val and 'gdc__project__project_id' in val and 'gdc__type' in val and 'gdc__aliquots__aliquot_id' in val:
            hits.append( "/experiment/source/"+val["source"]+"/program/"+val["gdc__program__name"].lower()+"/tumor/"+val["gdc__project__project_id"].lower()+"/datatype/"+val["gdc__type"].lower().replace("_","")+"/aliquot/"+val["gdc__aliquots__aliquot_id"].lower()+"/all" )
    data = {
        'attribute': attribute,
        'value': value,
        'hits': hits
    }
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/metadata/aliquot/<aliquot>/urls")
def metadata_aliquot(aliquot):
    mongodb_client = getClient()
    values = get_documents(mongodb_client, "metadata", find_attributes={ 'gdc__aliquots__aliquot_id': aliquot }, find_criteria={ 'source':1, 'gdc__program__name':1, 'gdc__project__project_id':1, 'gdc__type':1 }) #'source':1 non esiste questo campo
    hits = [ ]
    for val in values:
        if 'gdc__program__name' in val and 'gdc__project__project_id' in val and 'gdc__type' in val:
            hits.append( "/experiment/source/"+val["source"]+"/program/"+val["gdc__program__name"]+"/tumor/"+val["gdc__project__project_id"]+"/datatype/"+val["gdc__type"]+"/aliquot/"+aliquot+"/all" )
    data = {
        'aliquot': aliquot,
        'hits': hits
    }
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/metadata/attribute/<attribute>/value/<value>/aliquots")
def metadata_aliquot_list(attribute, value):
    mongodb_client = getClient()
    values = get_documents(mongodb_client, "metadata", find_attributes={ attribute: value }, find_criteria={ 'source':1, 'gdc__program__name':1, 'gdc__project__project_id':1, 'gdc__type':1, 'gdc__aliquots__aliquot_id':1 })
    data = {
        'attribure': attribute,
        'value': value,
        'hits': values
    }
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;
