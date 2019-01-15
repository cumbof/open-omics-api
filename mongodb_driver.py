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
def get_documents(client, collection_id, find_attributes={}, find_criteria={}, max_attempts=5):
    documents = [];
    if client not None:
        db = client[mongodb_db_name];
        collection = db[collection_id];
        try:
            for doc in collection.find( find_attributes, find_criteria ):
                documents.append( doc )
        except Exception as e:
            client.close();
            client = getClient();
            if max_attempts > 0:
                return get_documents(client, collection_id, find_criteria={}, max_attempts=max_attempts-1);
            else:
                print str(e);
                return [];
    return [];
