from flask import request, Response, session
from . import blueprint

# load data map
data_map = None;
with open("./data.yaml", 'r') as dmap:
    data_map = yaml.load(dmap);

@blueprint.route("/experiment/sources")
def experiment_sources():
    data = { 'sources': [ ] }
    for source in data_map['sources']:
        data['sources'].append( {
            'id': source['id'],
            'description': source['description']
        } )
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/experiment/datatypes")
def experiment_datatypes():
    data = { 'datatypes': [ ] }
    for datatype in data_map['datatypes']:
        data['datatypes'].append( {
            'id': datatype['id'],
            'description': datatype['description']
        } )
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/experiment/tumors")
def experiment_tumors():
    data = { 'tumors': [ ] }
    for tumor in data_map['tumors']:
        source_index = tumor['source']
        source_id = ''
        source_description = ''
        for source in data_map['sources']:
            if source['index'] == source_index:
                source_id = source['id']
                source_description = source['description']
                break
        program_index = tumor['program']
        program_id = ''
        program_description = ''
        for program in data_map['programs']:
            if program['index'] == program_index:
                program_id = program['id']
                program_description = program['description']
                break
        datatypes_indices = tumor['datatypes']
        datatypes = [ ]
        for datatype_index in datatypes_indices:
            for datatype in data_map['datatypes']:
                if datatype['index'] == datatype_index:
                    datatypes.append( {
                        'id': datatype['id'],
                        'description': datatype['description']
                    } )
                    break
        data['tumors'].append( {
            'id': tumor['id'],
            'description': tumor['description'],
            'source': {
                'id': source_id,
                'description': source_description
            },
            'program': {
                'id': program_id,
                'description': program_description
            }
            'datatypes': datatypes
        } )
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/experiment/programs")
def experiment_programs():
    data = { 'programs': [ ] }
    for program in data_map['programs']:
        source_index = program['source']
        source_id = ''
        source_description = ''
        for source in data_map['sources']:
            if source['index'] == source_index:
                source_id = source['id']
                source_description = source['description']
                break
        data['programs'].append( {
            'id': program['id'],
            'description': program['description'],
            'source': {
                'id': source_id,
                'description': source_description
            }
        } )
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/experiment/source/<source>/programs")
def experiment_source_programs(source):
    data = { 'programs': [ ] }
    for program in data_map['programs']:
        current_source_index = program['source']
        for source in data_map['sources']:
            if source['index'] == current_source_index and source['id'] == source:        
                data['programs'].append( {
                    'id': program['id'],
                    'description': program['description']
                } )
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/experiment/source/<source>/aliquots")
def experiment_source_aliquots(source):
    data = { 'aliquots': [ ] }
    source_index = -1
    for source_obj in data_map['sources']:
        if source_obj['id'] == source:
            source_index = source_obj['index']
            break
    if source_index > -1:
        tumors_related_to_source = [ tumor['id'] for tumor in data_map['tumors'] if tumor['source'] == source_index ]
        # TODO: get only available data types for those particular tumors
        collections = [ 'experiment_'+datatype['id'] for datatype in data_map['datatypes'] ]
        mongodb_client = getClient()
        aliquots = set()
        for collection in collections:
            for tumor in tumors_related_to_source:
                documents = get_documents(mongodb_client, collection, find_attributes={ 'tumor': tumor }, find_criteria={ 'aliquot':1 })
                aliquots.add( doc['aliquot'] for doc in documents )
        data['aliquots'] = list(aliquots)
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/experiment/source/<source>/datatypes")
def experiment_source_datatypes(source):
    data = { 'datatypes': [ ] }
    source_index = -1
    for source_obj in data_map['sources']:
        if source_obj['id'] == source:
            source_index = source_obj['index']
            break
    if source_index > -1:
        programs_indices = [ ]
        for program in data_map['programs']:
            if program['source'] == source_index:
                programs_indices.append( program['index'] )
        if len(programs_indices) > 0:
            for datatype in data_map['datatypes']:
                datatype_programs = datatype['programs']
                for datatype_program in datatype_programs:
                    if datatype_program in programs_indices:
                        data['datatypes'].append( {
                            'id': datatype['id'],
                            'description': datatype['description']
                        } )
                        break
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/experiment/source/<source>/tumors")
def experiment_source_tumors(source):
    data = { 'tumors': [ ] }
    source_index = -1
    for source_obj in data_map['sources']:
        if source_obj['id'] == source:
            source_index = source_obj['index']
            break
    if source_index > -1:
        for tumor in data_map['tumors']:
            if tumor['source'] == source_index:
                data['tumors'].append( {
                    'id': tumor['id'],
                    'description': tumor['description']
                } )
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/experiment/source/<source>/program/<program>/aliquots")
def experiment_source_program_aliquots(source, program):
    data = { 'aliquots': [ ] }
    source_index = -1
    for source_obj in data_map['sources']:
        if source_obj['id'] == source:
            source_index = source_obj['index']
            break
    program_index = -1
    for program_obj in data_map['programs']:
        if program_obj['id'] == program:
            program_index = program_obj['index']
            break
    if source_index > -1 and program_index > -1:
        tumors_related_to_source = [ tumor['id'] for tumor in data_map['tumors'] if tumor['source'] == source_index and tumor['program'] == program_index ]
        # TODO: get only available data types for those particular tumors
        collections = [ 'experiment_'+datatype['id'] for datatype in data_map['datatypes'] ]
        mongodb_client = getClient()
        aliquots = set()
        for collection in collections:
            for tumor in tumors_related_to_source:
                documents = get_documents(mongodb_client, collection, find_attributes={ 'tumor': tumor }, find_criteria={ 'aliquot':1 })
                aliquots.add( doc['aliquot'] for doc in documents )
        data['aliquots'] = list(aliquots)
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/experiment/source/<source>/program/<program>/datatypes")
def experiment_source_program_datatypes(source, program):
    data = { 'datatypes': [ ] }
    source_index = -1
    for source_obj in data_map['sources']:
        if source_obj['id'] == source:
            source_index = source_obj['index']
            break
    program_index = -1
    for program_obj in data_map['programs']:
        if program_obj['id'] == program and program_obj['source'] == source_index:
            program_index = program_obj['index']
            break
    if source_index > -1 and program_index > -1:
        for datatype in data_map['datatypes']:
            datatype_programs = datatype['programs']
            for datatype_program in datatype_programs:
                if datatype_program == program_index:
                    data['datatypes'].append( {
                        'id': datatype['id'],
                        'description': datatype['description']
                    } )
                    break
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/experiment/source/<source>/program/<program>/tumors")
def experiment_source_program_tumors(source, program):
    data = { 'tumors': [ ] }
    source_index = -1
    for source_obj in data_map['sources']:
        if source_obj['id'] == source:
            source_index = source_obj['index']
            break
    program_index = -1
    for program_obj in data_map['programs']:
        if program_obj['id'] == program and program_obj['source'] == source_index:
            program_index = program_obj['index']
            break
    if source_index > -1 and program_index > -1:
        for tumor in data_map['tumors']:
            if tumor['source'] == source_index and tumor['program'] == program_index:
                data['tumors'].append( {
                    'id': tumor['id'],
                    'description': tumor['description']
                } )
            break
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/experiment/source/<source>/program/<program>/tumor/<tumor>/datatypes")
def experiment_source_program_tumor_datatypes(source, program, tumor):
    data = { 'datatypes': [ ] }
    source_index = -1
    for source_obj in data_map['sources']:
        if source_obj['id'] == source:
            source_index = source_obj['index']
            break
    program_index = -1
    for program_obj in data_map['programs']:
        if program_obj['id'] == program and program_obj['source'] == source_index:
            program_index = program_obj['index']
            break
    if source_index > -1 and program_index > -1:
        tumor_found = False
        for tumor in data_map['tumors']:
            if tumor['source'] == source_index and tumor['program'] == program_index:
                datatype_programs = datatype['programs']
                for datatype_program in datatype_programs:
                    if datatype_program == program_index:
                        data['datatypes'].append( {
                            'id': datatype['id'],
                            'description': datatype['description']
                        } )
                        tumor_found = True
                        break
                if tumor_found:
                    break
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/experiment/source/<source>/program/<program>/tumor/<tumor>/aliquots")
def experiment_source_program_tumor_aliquots(source, program, tumor):
    data = { 'aliquots': [ ] }
    source_index = -1
    for source_obj in data_map['sources']:
        if source_obj['id'] == source:
            source_index = source_obj['index']
            break
    program_index = -1
    for program_obj in data_map['programs']:
        if program_obj['id'] == program:
            program_index = program_obj['index']
            break
    if source_index > -1 and program_index > -1:
        tumors_related_to_source = [ tumor_obj['id'] for tumor_obj in data_map['tumors'] if tumor_obj['source'] == source_index and tumor_obj['program'] == program_index ]
        if tumor in tumors_related_to_source:
            # TODO: get only available data types for that particular tumor
            collections = [ 'experiment_'+datatype['id'] for datatype in data_map['datatypes'] ]
            mongodb_client = getClient()
            aliquots = set()
            for collection in collections:
                documents = get_documents(mongodb_client, collection, find_attributes={ 'tumor': tumor }, find_criteria={ 'aliquot':1 })
                aliquots.add( doc['aliquot'] for doc in documents )
            data['aliquots'] = list(aliquots)
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/experiment/source/<source>/program/<program>/tumor/<tumor>/datatype/<datatype>/aliquots")
def experiment_source_program_tumor_datatype_aliquots(source, program, tumor, datatype):
    data = { 'aliquots': [ ] }
    source_index = -1
    for source_obj in data_map['sources']:
        if source_obj['id'] == source:
            source_index = source_obj['index']
            break
    program_index = -1
    for program_obj in data_map['programs']:
        if program_obj['id'] == program:
            program_index = program_obj['index']
            break
    datatype_index = -1
    for datatype_obj in data_map['datatypes']:
        if datatype_obj['id'] == datatype:
            datatype_index = datatype_obj['index']
            break
    if source_index > -1 and program_index > -1 and datatype_index > -1:
        tumors_related_to_source = [ tumor_obj['id'] for tumor_obj in data_map['tumors'] if tumor_obj['source'] == source_index and tumor_obj['program'] == program_index ]
        if tumor in tumors_related_to_source:
            # TODO: get only available data types for that particular tumor
            tumor_datatypes_indices = [ dt for dt in tumor_obj['datatypes'] for tumor_obj in data_map['tumors'] if tumor_obj['source'] == source_index and tumor_obj['program'] == program_index and tumor_obj['id'] == tumor ]
            if datatype in tumor_datatypes_indices:
                mongodb_client = getClient()
                aliquots = set()
                documents = get_documents(mongodb_client, datatype, find_attributes={ 'tumor': tumor }, find_criteria={ 'aliquot':1 })
                aliquots.add( doc['aliquot'] for doc in documents )
                data['aliquots'] = list(aliquots)
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/experiment/source/<source>/program/<program>/tumor/<tumor>/datatype/<datatype>/aliquot/<aliquot>/all")
def experiment_source_program_tumor_datatype_aliquot_all(source, program, tumor, datatype, aliquot):
    data = { 'data': [ ] }
    mongodb_client = getClient()
    # TODO: missed 'source' and 'program' in find_attributes
    elem_attribute = ""
    # TODO: excluded 'copynumbersegment' and 'maskedcopynumbersegment'
    annotation_collection = ""
    fields = {
        '_id': 0,
        'tumor': 0,
        'aliquot': 0,
        'source': 0
    }
    if datatype == "geneexpressionquantification":
        elem_attribute = "ensembl_gene_id"
        annotation_collection = "annotation_geneexpression"
        # exclude obj fields
        fields['annotations._id'] = 0
        # considering as_field = 'annotations'
        # exclude annotation fields
        fields['annotations.ensembl_gene_id'] = 0
    elif datatype == "methylationbetavalue":
        elem_attribute = "composite_element_ref"
        annotation_collection = "annotation_humanmethylation"
        # exclude obj fields
        fields['annotations._id'] = 0
        # considering as_field = 'annotations'
        # exclude annotation fields
        fields['annotations.composite_element_ref'] = 0        
    elif datatype == "maskedsomaticmutation":
        elem_attribute = "gene_symbol"
    elif datatype == "mirnaexpressionquantification" or datatype == "isoformexpressionquantification":
        elem_attribute = "mirna_id"
    
    if elem_attribute != "":
        if datatype == "geneexpressionquantification" or datatype == "methylationbetavalue":
            as_field = "annotations"
            match_field = {
                'source': source,
                'tumor': tumor,
                'aliquot': aliquot,
            }
            data['data'] = get_documents_by_join(mongodb_client, "experiment_"+datatype, annotation_collection, elem_attribute, elem_attribute, as_field, match_field, fields)
        else:
            data['data'] = get_documents(mongodb_client, "experiment"+datatype, find_attributes={ 'tumor': tumor, 'aliquot': aliquot }, find_criteria={ 'tumor':0, 'aliquot':0, 'source':0, '_id':0 })
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/experiment/source/<source>/program/<program>/tumor/<tumor>/datatype/<datatype>/aliquot/<aliquot>/coordinates")
def experiment_source_program_tumor_datatype_aliquot_coordinates(source, program, tumor, datatype, aliquot):
    data = { 'data': [ ] }
    collection_name = ""
    collection_from_name = ""
    fields = { '_id':0 }
    if datatype = "methylationbetavalue":
        collection_name = "annotation_humanmethylation"
        collection_from_name = "experiment_"+datatype
        fields['annotations.chrom'] = 1
        fields['annotations.start'] = 1
        fields['annotations.end'] = 1
        fields['annotations.strand'] = 1
    else:
        if datatype == "geneexpressionquantification":
            collection_name = "annotation_geneexpression"
        collection_name = "experiment_"+datatype
        fields['chrom'] = 1
        fields['start'] = 1
        fields['end'] = 1
        fields['strand'] = 1

    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/experiment/source/<source>/program/<program>/tumor/<tumor>/datatype/<datatype>/aliquot/<aliquot>/ids")
def experiment_source_program_tumor_datatype_aliquot_ids(source, program, tumor, datatype, aliquot):
    data = { 'ids': [ ] }
    mongodb_client = getClient()
    # TODO: missed 'source' and 'program' in find_attributes
    elem_attribute = ""
    # TODO: ids for 'copynumbersegment' and 'maskedcopynumbersegment' ?
    if datatype == "geneexpressionquantification":
        elem_attribute = "ensembl_gene_id"
    elif datatype == "methylationbetavalue":
        elem_attribute = "composite_element_ref"      
    elif datatype == "maskedsomaticmutation":
        elem_attribute = "gene_symbol"
    elif datatype == "mirnaexpressionquantification" or datatype == "isoformexpressionquantification":
        elem_attribute = "mirna_id"
    ids = set()
    documents = get_documents(mongodb_client, "experiment"+datatype, find_attributes={ 'tumor': tumor, 'aliquot': aliquot }, find_criteria={ elem_attribute:1 })
    ids.add( doc[elem_attribute] for doc in documents )
    data['ids'] = list(ids)
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/experiment/source/<source>/program/<program>/tumor/<tumor>/datatype/<datatype>/aliquot/<aliquot>/id/<elem_id>")
def experiment_source_program_tumor_datatype_aliquot_elemid_all(source, program, tumor, datatype, aliquot, elem_id):
    data = { 'data': [ ] }
    mongodb_client = getClient()
    # TODO: missed 'source' and 'program' in find_attributes
    elem_attribute = ""
    # TODO: excluded 'copynumbersegment' and 'maskedcopynumbersegment'
    annotation_collection = ""
    fields = {
        '_id': 0,
        'tumor': 0,
        'aliquot': 0,
        'source': 0
    }
    if datatype == "geneexpressionquantification":
        elem_attribute = "ensembl_gene_id"
        annotation_collection = "annotation_geneexpression"
        # exclude obj fields
        fields['annotations._id'] = 0
        # considering as_field = 'annotations'
        # exclude annotation fields
        fields['annotations.ensembl_gene_id'] = 0
    elif datatype == "methylationbetavalue":
        elem_attribute = "composite_element_ref"
        annotation_collection = "annotation_humanmethylation"
        # exclude obj fields
        fields['annotations._id'] = 0
        # considering as_field = 'annotations'
        # exclude annotation fields
        fields['annotations.composite_element_ref'] = 0        
    elif datatype == "maskedsomaticmutation":
        elem_attribute = "gene_symbol"
    elif datatype == "mirnaexpressionquantification" or datatype == "isoformexpressionquantification":
        elem_attribute = "mirna_id"
    
    if elem_attribute != "":
        if datatype == "geneexpressionquantification" or datatype == "methylationbetavalue":
            as_field = "annotations"
            match_field = {
                'source': source,
                'tumor': tumor,
                'aliquot': aliquot,
                elem_attribute: elem_id
            }
            # aggregate example (shell)
            '''
                db.experiment_collection.aggregate([
                    {
                        $lookup:
                        {
                            from: "annotation_collection",
                            localField: "elem_attribute",
                            foreignField: "elem_attribute",
                            as: "annotations"
                        }
                    }
                ])
            '''
            data['data'] = get_documents_by_join(mongodb_client, "experiment_"+datatype, annotation_collection, elem_attribute, elem_attribute, as_field, match_field, fields)
        else:
            data['data'] = get_documents(mongodb_client, "experiment"+datatype, find_attributes={ 'tumor': tumor, 'aliquot': aliquot, elem_attribute: elem_id }, find_criteria={ 'tumor':0, 'aliquot':0, 'source':0, '_id':0 })
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/experiment/aliquot/<aliquot>/list")
def experiment_aliquot_list(aliquot):
    mongodb_client = getClient()
    values = get_documents(mongodb_client, "metadata", find_attributes={ 'gdc__aliquots__aliquot_id': aliquot }, find_criteria={ 'source':1, 'gdc__program__name':1, 'gdc__project__project_id':1, 'gdc__type':1 })
    hits = [ ]
    for val in values:
        hits.append( "/experiment/source/"+val["source"]+"/program/"+val["gdc__program__name"]+"/tumor/"+val["gdc__project__project_id"]+"/datatype/"+val["gdc__type"]+"/aliquot/"+aliquot+"/all" )
    data = {
        'aliquot': aliquot,
        'hits': hits
    }
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;
