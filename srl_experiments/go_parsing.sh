#!/bin/bash
#--SAMPLES---
for nsamp in 10 100 greedy; do 
    for prefix in train test; do
        split -l 10000 data/${prefix}_sents.txt batch_${prefix}_sent_
        ls -1 batch_${prefix}_sent_* | parallel --eta -j10 "./parsetext.sh {} ${nsamp}"
    done 

    #move everything out then
    fldr=${nsamp}samp_batches
    mkdir $fldr
    mv batch* ${fldr} 
done 

#then concatenate
for nsamp in 10 100 greedy; do 
    for prefix in train test; do
        fldr=${nsamp}samp_batches
        cat ${fldr}/*${prefix}*.pred > ${fldr}/${prefix}_all.pred
    done
done
  




