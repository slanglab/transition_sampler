#!/bin/bash
mkdir logs preds  

#1. extract features from brendan's .pred samples and .conllu greedy parse 
./run_feat_extr.sh | tee logs/11-28_feats.log 

#2. then run thru the pf code 
cd ~/policefatalities_emnlp2017
TRAIN="data/sentments/train.json"
TEST="data/sentments/test.json"
DIR="/home/kkeith/parsemar/pf/feat_extract/feats"

for nsamp in 'greedy' 10 100; do 
    echo $nsamp 
    python code/models/logreg/runlr.py $TRAIN $TEST $DIR/${nsamp}_train.mtx $DIR/${nsamp}_test.mtx --emiters 0 | tee ${nsamp}_run.log
    #only evaluate the hard LR (no EM!)
    cat code/models/preds/em0.json | python code/eval/evaluation.py | tee ${nsamp}_results.log
    #copy em0 so I can access it again somewhere else
    cp code/models/preds/em0.json /home/kkeith/parsemar/pf/feat_extract/preds/${nsamp}_em0.json
done 

#====print out the results at the end so that they're easy to look at
for nsamp in 'greedy' 10 100; do
    echo "============"
    echo "===${nsamp} samp results"
    cat ${nsamp}_results.log
done