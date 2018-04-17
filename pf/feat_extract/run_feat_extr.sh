#!/bin/bash
mkdir feats_batches_100samp feats_batches_10samp feats

CORES=10
BIGDIR=/home/brenocon/parsemar/pf
for nsamp in 10 100; do
    INDIR=$BIGDIR/batches_${nsamp}samp 
    #ls -1 $INDIR/*.pred | parallel -v --dryrun "python extr_samp_feats.py {}"
    ls -1 $INDIR/*.pred | parallel --eta -j$CORES "python extr_samp_feats.py {} ${nsamp}"
done

#===then need to do the greedy files 
mkdir feats_batches_greedy
#both batches_10samp and batches_100samp have the same thing so doesn't matter which one we want 
INDIR=/home/brenocon/parsemar/pf/batches_10samp
#run in parallel 
#ls -1 $INDIR/*.pred | parallel -v --dryrun "python extr_samp_feats.py {}"
ls -1 $INDIR/*.conllu | parallel --eta -j$CORES "python extr_samp_feats.py {} 1 --greedy"

#===then concat the feat predictions
echo 'NOW FEATURE HASHING'
python feat_hash.py
echo "all .json feature files are in the feats/ directory" 



