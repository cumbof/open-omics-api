#!/usr/bin/env python3

__author__ = ('Fabio Cumbo (fabio.cumbo@unitn.it)')
__version__ = '0.01'
__date__ = 'Feb 22, 2021'

import os, requests
import argparse as ap

OPENOMICS_ENDPOINT_CPG = "http://bioinformatics.iasi.cnr.it/openomics/annotation/humanmethylation/id/{}"
OPENOMICS_ENDPOINT_OVERLAP = "http://bioinformatics.iasi.cnr.it/openomics/annotation/geneexpression/overlap/chrom/{}/start/{}/end/{}/strand/{}"
PDB_ENDPOINT_SEARCH = "https://search.rcsb.org/rcsbsearch/v1/query"
PDB_ENDPOINT_DOWNLOAD = "http://files.rcsb.org/download/"
PDB_CIF_MASK = "{}.cif.gz"

def read_params():
    p = ap.ArgumentParser( description = ( 'The CpgGenePdb.py script to extract gene symbols overlapping with input CpG site '
                                            'and retrieve PDB protein structures related to such genes' ),
                           formatter_class = ap.ArgumentDefaultsHelpFormatter )
    p.add_argument( '--composite_element_ref', 
                    type = str,
                    help = 'CpG Site ID' )
    p.add_argument( '--outdir', 
                    type = str,
                    help = 'Output folder path on which PDB Cif files will be located' )
    p.add_argument( '--verbose',
                    action = 'store_true',
                    default = False,
                    help = 'Print messages to STDOUT' )
    p.add_argument( '-v', 
                    '--version', 
                    action = 'version',
                    version = 'CpgGenePdb.py version {} ({})'.format( __version__, __date__ ),
                    help = "Print the current CpgGenePdb.py version and exit" )
    return p.parse_args()

def query( url, params={}, method="GET", repeat=0 ):
    # Make a query to the API with payload
    recursion_count = 0
    query_response = { }
    while recursion_count <= repeat:
        try:
            if method == "GET":
                response = requests.get( url, headers={"Content-Type": "application/json"} )
            elif method == "POST":
                response = requests.post( url, headers={"Content-Type": "application/json"}, json=params )
            response.raise_for_status()
            query_response = response.json()
            break
        except:
            # Repeat
            recursion_count += 1
    return query_response

def download( url, filepath ):
    try:
        response = requests.get( url, allow_redirects=True )
        response.raise_for_status()
        open( filepath, 'wb' ).write( response.content )
        return True
    except:
        return False

if __name__ == '__main__':
    # Init params
    args = read_params()

    # Init output folder if it does not exist
    if not os.path.exists( args.outdir ):
        os.makedirs( args.outdir )

    # Input CpG Site ID
    cpg = args.composite_element_ref
    openomics_cpg = OPENOMICS_ENDPOINT_CPG.format( cpg )
    if args.verbose:
        print( "Composite Element Ref: {}".format( cpg ) )
        print( "Searching for CpG island" )
        print( "\tQuerying {}".format(openomics_cpg) )
    # Get CpG Site info
    cpg_info = query( openomics_cpg )
    if 'id' in cpg_info:
        if cpg_info['id'][0]:
            # Get CpG Site genomic coordinates
            chrom = cpg_info['id'][0]["chrom"]
            start = int(cpg_info['id'][0]["start"])
            end = int(cpg_info['id'][0]["end"])
            strand = cpg_info['id'][0]["strand"]
            # Search for known overlapping gene symbols:
            #   This endpoint can in general retrieve multiple genes
            #   but CpG coordinates refer to a single position, so
            #   one gene only is expected to be retrieved
            openomics_overlap = OPENOMICS_ENDPOINT_OVERLAP.format( chrom, start, end, strand )
            if args.verbose:
                print( "\t\tChr:\t{}".format(chrom) )
                print( "\t\tStart:\t{}".format(start) )
                print( "\t\tEnd:\t{}".format(end) )
                print( "\t\tStrand:\t{}".format(strand) )
                print( "\tSearching for overlapping gene region" )
                print( "\t\tQuerying {}".format(openomics_overlap) )
            gene_info = query( openomics_overlap )
            if 'hits' in gene_info:
                if not gene_info['hits']:
                    if args.verbose:
                        print( "\t\tNo results found" )
                else:
                    gene_symbol = gene_info['hits'][0]['gene_symbol']
                    if args.verbose:
                        print( "\t\tOverlapping Gene Symbol: {}".format( gene_symbol ) )
                        print( "\t\tPDB Search Criteria: Gene Name = {}".format( gene_symbol ) )
                    pdb_payload = {
                                    "query": {
                                        "type": "terminal",
                                        "service": "text",
                                        "node_id": 0,
                                        "parameters": {
                                            "attribute": "rcsb_entity_source_organism.rcsb_gene_name.value",
                                            "operator": "in",
                                            "value": [
                                                gene_symbol
                                            ]
                                        }
                                    },
                                    "return_type": "entry",
                                    "request_options": {
                                        "pager": {
                                            "start": 0,
                                            "rows": 100
                                        },
                                        "scoring_strategy": "combined",
                                        "sort": [
                                            {
                                                "sort_by": "score",
                                                "direction": "desc"
                                            }
                                        ]
                                    }
                                  }
                    pdb_hits = query( PDB_ENDPOINT_SEARCH, params=pdb_payload, method="POST" )
                    if not pdb_hits:
                        if args.verbose:
                            print( "\t\t\tNo results found" )
                    else:
                        for hit in pdb_hits["result_set"]:
                            structure_id = hit["identifier"]
                            cif_pdb_path = "{}{}".format( PDB_ENDPOINT_DOWNLOAD, PDB_CIF_MASK.format(structure_id) )
                            cif_local_path = os.path.join( args.outdir, PDB_CIF_MASK.format(structure_id) )
                            if args.verbose:
                                print( "\t\t\tDownloading {}".format(cif_pdb_path) )
                            if not download( cif_pdb_path, cif_local_path ):
                                if args.verbose:
                                    print( "\t\t\t\t[Error] Unable to download PDB Structure {}".format( structure_id ) )
