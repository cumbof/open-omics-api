#APIs use case able to count the number of distinct DNA somatic mutations available 
#on all the experimental data in our database. This count is grouped by the ethnicity 
#of the patients on which a this kind of experiment has been performed.
import json, urllib.request
apis_base_url = 'http://bioinformatics.iasi.cnr.it/'
source = 'gdc'
datatype = 'maskedsomaticmutation'

# retrieve all the ethnicities in the 'metadata' collection
ethnicity_attribute = 'gdc__demographic__ethnicity'
ethnicities = json.loads( urllib.request.urlopen(
                        '{}/metadata/source/{}/attribute/{}/all'
                            .format(apis_base_url, source, ethnicity_attribute)
              ).read() )

for ethnicity_value in ethnicities['values']:
    distinct_somatic_mutations = list()
    # retrieve aliquots related to the current ethnicity
    aliquots = json.loads( urllib.request.urlopen(
                    '{}/metadata/source/{}/attribute/{}/value/{}/aliquots'
                        .format(apis_base_url, source, ethnicity_attribute, ethnicity_value)
               ).read() )
    
    for aliquot_url in aliquots['hits']:
        if '/datatype/{}'.format(datatype) in aliquot_url:
            coords_position = aliquot_url.rfind('all')
            coords_url = '{}coordinates'.format(aliquot_url[:coords_position])
            # extract the somatic mutation positions available
            # in the experiment related to the current aliquot
            coords_list = json.loads( urllib.request.urlopen(
                                    apis_base_url+
                                    coords_url
                          ).read() )
            for coordinates in coords_list['coordinates']:
                coords_arr = [
                    coordinates['chrom'], coordinates['start'],
                    coordinates['end'], coordinates['strand']
                ]
                if coords_arr not in distinct_somatic_mutations:
                    distinct_somatic_mutations.append(coords_arr)
    
    print( 'Number of distinct somatic mutation for the ethnicity {} is {}'.format( 
                ethnicity_value, 
                len(distinct_somatic_mutations) 
         ) )