#Use case scenario in which the patient id related to a provided experimental aliquot id is extracted. 
#This patient id is used to retrieve all the experiments conducted on the same patient.

import json, urllib.request
apis_base_url = 'http://bioinformatics.iasi.cnr.it/'
aliquot_attribute = 'gdc__aliquots__aliquot_id'
aliquot_value = '00168e86-d23a-48ae-8c60-36d970051907'
patient_attribute = 'biospecimen__shared__bcr_patient_barcode'

# retrieve the patient id related to the specified aliquot
patient_barcode = json.loads( urllib.request.urlopen(
                        apis_base_url+
                        '/metadata/attribute/{}/value/{}/list'
                        .format(aliquot_attribute,
                                aliquot_value)
                  ).read() )[ 'hits' ][ 0 ][ patient_attribute ]

# extract all the experiments related to the patient barcode
for aliquot in json.loads( urllib.request.urlopen(
                    apis_base_url+
                    '/metadata/attribute/{}/value/{}/aliquots'
                    .format(patient_attribute, patient_barcode)
               ).read() )[ 'hits' ]:
    print( aliquot )