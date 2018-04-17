#!/bin/bash
cp /home/brenocon/parsemar/pf/allsent_* ./ 

for f in allsent_*; do
    cat $f | grep '"docid":' | cut -f 1 -d$'\t' --complement > dicts_$f
    echo dicts_$f
done

