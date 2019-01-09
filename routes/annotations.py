from flask import request, Response, session
from . import blueprint

import datetime, pytz
from db import *
from functions import *
from batch_manager import *

__VALID_CHARS__ = '.-()[]0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ';

# load config
config = None;
with open("./config.yaml", 'r') as cfg:
    config = yaml.load(cfg);
tmp_dir = str(config.get("app", "tmp_dir"));

@blueprint.route("/tree")
def tree():
    data = {
        'trees': [ ]
    };
    for tree_obj in query_db('select * from trees'):
        tree_id = tree_obj[0];
        accessions_count = len(query_db('select accession_number from accessions where tree_id=\''+tree_id+'\''));
        tree = {
            'tree_id': tree_id,
            'tree_name': tree_obj[1],
            'accessions_count': accessions_count
        };
        data['trees'].append(tree);
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

# @app.route('/tree/<int:tree_id>')
# @app.route('/tree/<float:tree_id>')
# @app.route('/tree/<path:tree_id>')
# The default is string which accepts any text without slashes.
#app.route("/tree/<tree_id>")
#@limiter.exempt
def tree_info(tree_id):
    tree = { };
    for tree_obj in query_db('select * from trees where tree_id=\''+tree_id+'\''):
        tree['tree_id'] = tree_obj[0];
        tree['tree_name'] = tree_obj[1];
        tree['accessions_count'] = len(query_db('select accession_number from accessions where tree_id=\''+tree_id+'\''));
        tree['rrr'] = {
            'path': tree_obj[2]
        };
        tree['roar'] = {
            'path': tree_obj[3]
        };
        tree['hashfile_absolute_path'] = tree_obj[4];
    #js = json.dumps(tree, indent=4, sort_keys=True);
    #resp = Response(js, status=200, mimetype='application/json');
    #return resp;
    return tree;

@blueprint.route("/tree/<tree_id>/accession")
def tree_accession(tree_id):
    data = {
        'tree_id': tree_id,
        'accessions_count': 0,
        'accessions' : [ ]
    };
    accessions_count = 0;
    for accession_obj in query_db('select * from accessions where tree_id=\''+tree_id+'\''):
        accession_number = accession_obj[2];
        data['accessions'].append(accession_number);
        accessions_count = accessions_count + 1;
    data['accessions_count'] = accessions_count;
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/tree/<tree_id>/accession/<accession_number>")
def tree_accession_info(tree_id, accession_number):
    data = {
        'tree_id': tree_id,
        'accession_number': accession_number
    };
    for accession_obj in query_db('select * from accessions where tree_id=\''+tree_id+'\' and accession_number=\''+accession_number+'\''):
        data['source_id'] = accession_obj[3];
        data['download_timestamp'] = accession_obj[4];
    js = json.dumps(data, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;

@blueprint.route("/tree/<tree_id>/query", methods = ["POST"])
def tree_query(tree_id):
    #submitted_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S');
    submitted_timestamp = datetime.datetime.now(tz=pytz.utc).isoformat();
    # {rrr ; roar}
    search_mode = "rrr";
    # search threshold
    search_threshold = 0.7;
    # {0:disabled ; 1:enabled} [roar]
    exact_algorithm = 0;
    # {0:do not sort result ; 1:sort result}
    sort_result = 1;
    # sequences
    #sequences = { };
    sequences = "";
    req_json = request.get_json();

    for arg in req_json:
        if arg == "search_mode":
            search_mode = str(req_json[arg]);
        elif arg == "search_threshold":
            search_threshold = float(req_json[arg]);
        elif arg == "exact_algorithm":
            exact_algorithm = int(req_json[arg]);
        elif arg == "sort":
            sort_result = int(req_json[arg]);
        else:
            # The ID can contain alphanumeric characters in addition to spaces, dots, dashes, and round and square brackets.
            # Any additional character will be trimmed out.
            seq_id = ''.join(e for e in str(arg) if e in __VALID_CHARS__);
            seq_content = str(req_json[arg]);
            if seq_content.strip() != "":
                sequences = sequences + seq_content + "\n";

    # if sequences is not empty
    #if not sequences is False:
    sequences = sequences.strip();
    if sequences is not "":
        # create tmp query file
        query_id, tmp_query_file_path = createTmpQueryFile(tmp_dir, sequences.strip());
        # initialize tmp query result file (empty)
        tmp_query_res_file_path = initializeTmpQueryResultFile(tmp_dir, query_id);
        # retrieve tree and hashfile paths with api
        #tree_info_json = json.loads(tree_info(tree_id).data);
        tree_info_json = tree_info(tree_id);
        if len(tree_info_json) > 0:
            sbt_xxx_file_path = tree_info_json[search_mode]["path"];
            hashfile_path = tree_info_json["hashfile_absolute_path"];
            if sbt_xxx_file_path.strip() is not "":
                # take trace of the user
                if "user_email" in session:
                    user_email = session["user_email"];
                    query_db('insert into userqueries (user_email, query_id) values (\''+str(user_email)+'\', \''+str(query_id)+'\');');
                # queue query
                query_db('insert into queries (query_id, query_file_path, processed, status_msg, submitted_timestamp, result_file_path, search_mode, sbt_file_path, search_threshold, exact_algorithm, sort_result) values (\''+str(query_id)+'\', \''+str(tmp_query_file_path)+'\', 0, \'WAITING\', \''+str(submitted_timestamp)+'\', \''+str(tmp_query_res_file_path)+'\', \''+str(search_mode)+'\', \''+str(sbt_xxx_file_path)+'\', \''+str(search_threshold)+'\', '+str(exact_algorithm)+', '+str(sort_result)+');');
                queueQuery(str(query_id), req_json, search_mode, sbt_xxx_file_path, hashfile_path, tmp_query_file_path, tmp_query_res_file_path, search_threshold, exact_algorithm, sort_result);
                sub_data = {
                    'message': 'The query has been submitted',
                    'query_id': query_id,
                    'type': 'Success',
                    'status': 200
                };
                js = json.dumps(sub_data, indent=4, sort_keys=True);
                resp = Response(js, status=200, mimetype='application/json');
                return resp;
            else:
                err_data = {
                    'message': 'Unsupported search_mode for the specified tree',
                    'type': 'Error',
                    'status': 400
                }
                js = json.dumps(err_data, indent=4, sort_keys=True);
                resp = Response(js, status=400, mimetype='application/json');
                return resp;
        else:
            err_data = {
                'message': 'Invalid tree_id parameter',
                'type': 'Error',
                'status': 400
            }
            js = json.dumps(err_data, indent=4, sort_keys=True);
            resp = Response(js, status=400, mimetype='application/json');
            return resp;
    else:
        err_data = {
            'message': 'No sequences submitted',
            'type': 'Error',
            'status': 400
        }
        js = json.dumps(err_data, indent=4, sort_keys=True);
        resp = Response(js, status=400, mimetype='application/json');
        return resp;

@blueprint.route('/status/<query_id>')
def query_status(query_id):
    response = getStatus(tmp_dir, query_id);
    js = json.dumps(response, indent=4, sort_keys=True);
    resp = Response(js, status=200, mimetype='application/json');
    return resp;
