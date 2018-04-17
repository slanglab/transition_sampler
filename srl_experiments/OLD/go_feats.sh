#!/bin/bash
mkdir feats 
rm commands.txt
touch commands.txt

for nsamps in 10 100 greedy; do
    for mode in train test; do 
        echo -e "python get_feats.py ${nsamps} ${mode}" >> commands.txt 
        #printf instead?? 
    done 
done

#run in parallel 
parallel --v --dryrun < commands.txt
parallel --eta -j4 < commands.txt