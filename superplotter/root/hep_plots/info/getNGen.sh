#!/bin/bash

#file="smcwslep.txt"
#
#for file in ${file}
#do
#    FILE_LINES=`cat ${file}`
#    for line in ${FILE_LINES}
#    do    
#        echo Getting logicalDataSetName for dsid ${line}
#        ami list datasets --project mc12_8TeV --type EVNT --dataset-number ${line} >> logicalDataSetNames.txt
#    done
#done

# Get the number of events at the generator level (evgen)

#file="logicalDataSetNames.txt"
#file="smcwslep_full.txt"
file="smcwslep.txt"
for file in ${file}
do
    FILE_LINES=`cat ${file}`
    for dsid in ${FILE_LINES}
    do
        echo Getting generated events for ${dsid}
        echo Getting dataset name
        dsname=$(ami list datasets --project mc12_8TeV --type EVNT --dataset-number ${dsid})
        echo Dataset: ${dsname}
        neventLine=$(ami show dataset info ${dsname[0]} |grep "totalEvents")
       # neventLine=$(ami show dataset info ${line} |grep "totalEvents")
        neventArray=($neventLine)
        nEvents="${neventArray[2]}"
        
        echo "  nEvents: $nEvents"
        echo ${dsid}" "$nEvents >> model_NGen.txt
    done
done
