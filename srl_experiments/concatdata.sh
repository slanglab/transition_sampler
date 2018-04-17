#!/bin/bash
mkdir data 
FLDR=/data/ontonotes5_conll_format/data

for d in $FLDR/*/; do
    out=$(basename $d)
    f=$(find $d -name '*conll')
    cat $f >> data/${out}.txt
done 
