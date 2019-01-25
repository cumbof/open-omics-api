import os, re, pymongo
import xml.etree.ElementTree as ET

ftp_root_base_path = "/FTP/ftp-root/opengdc/bed/"
annotation_base_path = ftp_root_base_path + "_annotations/"
experiment_base_path = ftp_root_base_path + "tcga/"

exclude_idx_map = {
    "gene_expression_quantification": [ 0, 1, 2, 3, 5, 6, 7 ],
    "isoform_expression_quantification": [ ],
    "methylation_beta_value": [ 0, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17 ],
    "mirna_expression_quantification": [ ],
    "masked_somatic_mutation": [ ],
    "copy_number_segment": [ ],
    "masked_copy_number_segment": [ ]
}

client = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = client["og"]

def poputate_experiments(mydb, experiment_base_path):
    coll2indexMap = { }
    for subdir_base, dirs_base, files_base in os.walk( experiment_base_path ):
        for tumor_dir in dirs_base:
            tumor_dir_path = os.path.join(subdir_base, tumor_dir)
            for subdir_tumor, datatype_dirs, datatype_files in os.walk( tumor_dir_path ):
                for datatype_dir in datatype_dirs:
                    if datatype_dir.lower().strip() != "clinical_and_biospecimen_supplements":
                        exp_collection = mydb[ "experiment_" + datatype_dir.lower().replace("_", "") ]
                        meta_collection = mydb[ "metadata" ]
                        datatype_dir_path = os.path.join(tumor_dir_path, datatype_dir)
                        print('--------------------'+'\ndata processing from '+datatype_dir_path)
                        for subdir, dirs, files in os.walk( datatype_dir_path ):
                            bed_file_path = None
                            meta_file_path = None
                            schema_file_path = os.path.join(datatype_dir_path, 'header.schema')
                            schema_attributes, schema_types = get_schema_from_XML(schema_file_path)
                            for file in files:
                                if file.endswith(".bed"):
                                    bed_file_path = os.path.join(datatype_dir_path, file)
                                    additional_values = {
                                        "tumor": tumor_dir.lower(),
                                        "aliquot": "-".join(os.path.splitext(file)[0].split("-")[:-1]),
                                        "source": "gdc"
                                    }
                                    exp_docs = create_documents(bed_file_path, schema_attributes, schema_types, exclude_idx=exclude_idx_map[datatype_dir], additional_entries=additional_values)
                                    exp_collection.insert_many(exp_docs)
                                    indexMap["experiment_" + datatype_dir.lower().replace("_", "")] = { }
                                    for attr in schema_attributes:
                                        indexMap["experiment_" + datatype_dir.lower().replace("_", "")][attr] = 1
                                    print('bed: ' + file)                           
                                elif file.endswith(".meta"):
                                    meta_file_path = os.path.join(datatype_dir_path, file)
                                    meta_doc = create_meta_document(meta_file_path)
                                    meta_collection.insert_one(meta_doc)
                                    indexMap["metadata"] = { "gdc__aliquots__aliquot_id": 1 }
                                    for attr in schema_attributes:

                                    print('meta: ' + file)
    for collection_name in indexMap:
        createIndex(collection_name, indexMap[collection_name])
                            
def populate_annotations(mydb, annotation_base_path):
    for subdir_base, dirs_base, files_base in os.walk( annotation_base_path ):
        for annotation_dir in dirs_base:
            collection_name = re.sub(r'\d+', '', annotation_dir.lower())
            collection = mydb[ "annotation_" + collection_name ]
            annotation_dir_path = os.path.join(subdir_base, annotation_dir)
            indexMap = { }
            for subdir, dirs, files in os.walk( annotation_dir_path ):
                bed_file_path = None
                schema_file_path = None
                for file in files:
                    if file.endswith(".bed"):
                        bed_file_path = os.path.join(annotation_dir_path, file)
                    elif file.endswith(".schema"):
                        schema_file_path = os.path.join(annotation_dir_path, file)
                schema_attributes, schema_types = get_schema_from_XML(schema_file_path)
                for attr in schema_attributes:
                    indexMap[attr] = 1
                docs = create_documents(bed_file_path, schema_attributes, schema_types)
                collection.insert_many(docs)
            createIndex("annotation_"+collection_name, indexMap)

# https://docs.mongodb.com/manual/reference/method/db.collection.createIndexes/
def createIndex(collection_name, indexMap):
    collection = mydb[ collection_name ]
    indexes = [ ]
    for idx in indexMap:
        if indexMap[idx] > 0:
            indexes.append( pymongo.IndexModel( [ (idx, pymongo.ASCENDING) ], name=collection_name+"_"+idx ) )
    collection.create_indexes( indexes )

def create_documents(bed_file_path, schema_attributes, schema_types, exclude_idx=[], additional_entries={}):
    docs = []
    with open(bed_file_path) as bad_file:
        for line in bad_file:
            if line.strip() != "":
                splitted_line = line.split('\t')
                doc = { }
                for attr_index in range(0, len(splitted_line)): 
                    if attr_index not in exclude_idx:
                        if schema_types[ attr_index ] == "LONG":
                            doc[ schema_attributes[attr_index] ] = long(splitted_line[attr_index].strip())
                        elif schema_types[ attr_index ] == "DOUBLE":
                            doc[ schema_attributes[attr_index] ] = float(splitted_line[attr_index].strip())
                        else:
                            doc[ schema_attributes[attr_index] ] = str(splitted_line[attr_index].strip())
                        for additional_attr in additional_entries:
                            doc[ additional_attr ] = str(additional_entries[additional_attr])
                docs.append(doc)
    return docs

def create_meta_document(meta_file_path):
    doc = { }
    with open(meta_file_path) as meta_file:
        for line in meta_file:
            if line.strip() != "":
                splitted_line = line.split('\t')
                attribute = splitted_line[0].strip()
                values = splitted_line[1].strip()
                splitted_values = values.split(',')
                if len(splitted_values) > 1:
                   values = [v for v in splitted_values] 
                doc[attribute] = values
    return doc

# return array with attributes of the schema
def get_schema_from_XML(schema_file_path):
    tree = ET.parse(schema_file_path)
    root = tree.getroot()
    attributes = [ ]
    types = [ ]
    for child in root[0]:
        attributes.append( child.text )
        types.append( child.attrib["type"] )
    return attributes, types

if __name__ == '__main__':
    populate_annotations(mydb, annotation_base_path)
    poputate_experiments(mydb, experiment_base_path)
