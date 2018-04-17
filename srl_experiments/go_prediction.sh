#!/bin/bash

#TRAINING, GET FEATURES! 
mkdir feats 
rm commands.txt
touch commands.txt

for nsamps in 10 100 greedy; do
    echo -e "python train.py ${nsamps}" >> commands.txt 
done

#run in parallel 
parallel --v --dryrun < commands.txt
parallel --eta -j4 < commands.txt

#then predict on the test set
mkdir accs
rm commands.txt
touch commands.txt 

for nsamps in 10 100 greedy; do
    echo -e "python test.py ${nsamps}" >> commands.txt 
done

#run in parallel 
parallel --v --dryrun < commands.txt
parallel --eta -j4 < commands.txt


