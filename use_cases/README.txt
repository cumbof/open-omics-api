We provide three simple use cases, in which we adopt the Python 3 programming language to interact with our APIs. 

The first one shows how to count the distinct DNA somatic mutations in each group of ethnicity independently from the programs and related tumors. It exploits only three endpoints for (i) the identification of the ethnicities of the patients related to experiments stored in our database, (ii) the retrieval of the aliquots related to the experiments conducted on patients with the previously extracted ethnicities, and (iii) the extraction of the DNA somatic mutation experiments related to the extracted aliquots, and finally count the distinct number of DNA somatic mutations.

The second use case shows instead how to easily find the methylated sites (targets) overlapped to a specified genomic coordinate (source), exploiting only one endpoint. It is worth noting that both the source and targets coordinates can refer to particular gene, or isoform, or somatic mutation regions.

The last use case illustrates a scenario in which, starting from a given experimental aliquot id, all the experiments conducted on the same patient related to the specified aliquot are retrieved
