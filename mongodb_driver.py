import os
import yaml
import json
from pymongo import *
import os, subprocess

config = None;
with open("./dbss.yaml", 'r') as cfg:
    config = yaml.load(cfg);
mongodb_dir = config["mongodb"]["install_dir"];
mongodb_host = config["mongodb"]["host"];
mongodb_port = int(config["mongodb"]["port"]);
mongodb_db_name = config["mongodb"]["db_name"];

# the default document size in MongoDB is 16MB
#document_size_limit = 14680064 # (in bytes) 14MB

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

# insert documents in bulk mode
# optype: {insert, update}
def createBulk(arr, optype, query, update=None, upsert=True):
    if arr is None:
        arr = [ ];
    if optype == "insert":
        arr.append(InsertOne(query));
    elif optype == "update":
        arr.append(UpdateOne(query, update, upsert=upsert));
    return arr;

# execute the bulk
def runBulk(client, arr, collection_id, max_attempts=5):
    #client = getClient();
    if client is not None:
        db = client[mongodb_db_name];
        #collection = db[mongodb_collection_name];
        collection = db[collection_id];
        try:
            collection.bulk_write(arr, ordered=False);
        except Exception as e:
            client.close();
            client = getClient();
            if max_attempts > 0:
                return runBulk(client, arr, collection_id, max_attempts=max_attempts-1);
            else:
                print str(e);
                return client, False;
        return client, True;
    return client, False;

# get stuff
'''
def getKmerExperiments(client, collection_id, kmer_str, exists=False, experiment=None, max_attempts=5):
    experiments = [ ];
    #client = getClient();
    if client is not None:
        db = client[mongodb_db_name];
        #collection = db[mongodb_collection_name];
        collection = db[collection_id];
        try:
            verified = False;
            for kmer in collection.find( { "kmer": kmer_str }, { "_id": "0", "experiments": "1" } ):
                if not exists:
                    #experiments.append( kmer["experiment"] );
                    experiments.extend( kmer["experiments"] );
                else:
                    if kmer["experiments"] == experiment:
                        verified = True;
            if exists:
                return verified;
        except Exception as e:
            client.close();
            client = getClient();
            if max_attempts > 0:
                return getKmerExperiments(client, collection_id, kmer_str, exists=exists, experiment=experiment, max_attempts=max_attempts-1);
            else:
                print str(e);
                return client, experiments;
    return client, experiments;

def getExperiments(client, max_attempts=5):
    experiments = { };
    #client = getClient();
    if client is not None:
        db = client[mongodb_db_name];
        collection = db["experiments"];
        try:
            for exp in collection.find( { }, { "_id": "0", "name": "1", "organism": "1" } ):
                experiments[exp["name"]] = exp["organism"];
        except Exception as e:
            client.close();
            client = getClient();
            if max_attempts > 0:
                return getExperiments(client, max_attempts=max_attempts-1);
            else:
                print str(e);
                return client, experiments;
    return client, experiments;

def createIndex(client, collection_id, field, max_attempts=5):
    #client = getClient();
    if client is not None:
        db = client[mongodb_db_name];
        collection = db[collection_id];
        try:
            collection.create_index( [(field, ASCENDING)], unique=True );
        except Exception as e:
            client.close();
            client = getClient();
            if max_attempts > 0:
                return createIndex(client, collection_id, field, max_attempts=max_attempts-1);
            else:
                print str(e);
                return client;
    return client;
'''
