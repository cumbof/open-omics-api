#This use case show how to exploit our APIs to identify the methylated sites overlapped to a specific genomic region.
#This is performed by providing a chromosome, start position, end position, and strand of the such region.

import json, urllib.request
apis_base_url = 'http://bioinformatics.iasi.cnr.it/'
annotation = 'humanmethylation'
# genomic coordinates of the WASH7P gene
wash7p = [ 'chr1', 14404, 29570, '-' ]

# extract methylated site coordinates overlapped to WASH7P
for overlap in = json.loads( urllib.request.urlopen(
                    apis_base_url+
                    '/annotation/{}/overlap/chrom/{}/'+
                    'start/{}/end/{}/end/{}/strand/{}'
                    .format(annotation, wash7p[0], wash7p[1],
                        wash7p[2], wash7p[3])
                 ).read() )[ 'hits' ]:
    print( str( hit ) )