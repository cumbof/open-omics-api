import os
import yaml
import json
from pymongo import *
import os, subprocess

config = None;
with open("./config.yaml", 'r') as cfg:
    config = yaml.load(cfg);
mongodb_dir = config["mongodb"]["install_dir"];
mongodb_host = config["mongodb"]["host"];
mongodb_port = int(config["mongodb"]["port"]);
mongodb_db_name = config["mongodb"]["db_name"];

def startMongod():
    try:
        mongod_path = os.path.join(mongodb_dir, "mongod");
        mongod = subprocess.Popen( [ mongod_path ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT );
        return mongod;
    except:
        print "an error has occurred during mongod initialization"
        return None;

def restartMongod(mongod):
    terminateMongod(mongod)
    print "restarting mongod";
    return startMongod();

def terminateMongod(mongod):
    try:
        mongod.terminate();
    except:
        print "an error has occurred during mongod process kill"
        pass;

# True:running, False:terminated
def isMongodAlive(mongod):
    try:
        if mongod.poll() == None:
            return True;
    except:
        print "unable to communicate with mongod.. is it still alive?"
        pass;
    return False;

def getClient():
    return MongoClient(mongodb_host, mongodb_port);

# get stuff
def get_documents(client, collection_id, find_attributes={}, find_criteria={}, get_one_element=None, max_attempts=5, display_obj_ids=0):
    documents = [ ];
    find_criteria['_id'] = display_obj_ids;
    if client is not None:
        db = client[mongodb_db_name];
        collection = db[collection_id];
        try:
            if get_one_element is None:
                for doc in collection.find( find_attributes, find_criteria ):
                    documents.append( doc )
            else:
                documents_tmp = set()
                for doc in collection.find( find_attributes, find_criteria ):
                    documents_tmp.add( doc[ get_one_element ] )
                documents = list(documents_tmp)
        except Exception as e:
            client.close();
            client = getClient();
            if max_attempts > 0:
                return get_documents(client, collection_id, find_attributes=find_attributes, find_criteria=find_criteria, get_one_element=get_one_element, max_attempts=max_attempts-1, display_obj_ids=display_obj_ids);
            else:
                print str(e);
                return [ ];
    return documents;

def get_documents_by_join(client, current_collection_id, from_collection_id, local_field, foreign_field, as_field, match_field, fields, max_attempts=5):
    # match_field = { 'aliquot': 'XXXXXXXX', 'tumor': 'XXXXXXXX' }
    # fields = { 'chrom':1, 'start':1, ... }
    documents = [ ]
    if client is not None:
        pipeline = [
            { 
                '$lookup':
                    {
                        'from': from_collection_id,
                        'localField': local_field,
                        'foreignField': foreign_field,
                        'as': as_field
                    }
            },
            { '$unwind': '$'+as_field },
            { '$match': match_field },
            { '$project': fields }
        ]
        db = client[mongodb_db_name]
        collection = db[current_collection_id]
        try:
            for doc in collection.aggregate( pipeline ):
                tmp_doc = { }
                for attr in doc:
                    if attr != as_field:
                        tmp_doc[attr] = doc[attr]
                as_dict = doc[as_field][0]
                new_doc = dict(tmp_doc.items() + as_dict.items())
                documents.append( new_doc )
        except Exception as e:
            client.close();
            client = getClient();
            if max_attempts > 0:
                return get_documents_by_join(client, current_collection_id, from_collection_id, local_field, foreign_field, as_field, match_field, fields, max_attempts=max_attempts-1);
            else:
                print str(e);
                return [ ];
    return documents
