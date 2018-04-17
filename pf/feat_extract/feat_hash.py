from __future__ import division
from collections import defaultdict
import ujson as json
from sklearn.feature_extraction import FeatureHasher
import argparse, os
from scipy import sparse, io
from extrfeats import go_feathash

#need to concat all the parallel scripts that have been concatenated 

MAX_FEATS = 450000 #change based on the dimension you wish to feature hash to 

nsamp_list = ['10', '100', 'greedy']

allfeats = {k: defaultdict(list) for k in nsamp_list}
for nsamp in ['10', '100']:
    feat_dir = 'feats_batches_{0}samp'.format(nsamp)
    for fname in sorted(os.listdir(feat_dir)): #TODO how to double check that these are in the correct order that corresponds to the input?? 
        mode = fname.split('_')[1]
        feats = json.load(open(feat_dir+'/'+fname, 'r'))
        allfeats[nsamp][mode] += feats 

feat_dir = 'feats_batches_greedy'
nsamp = 'greedy'
for fname in sorted(os.listdir(feat_dir)): #TODO how to double check that these are in the correct order that corresponds to the input?? 
    mode = fname.split('_')[1]
    feats = json.load(open(feat_dir+'/'+fname, 'r'))
    allfeats[nsamp][mode] += feats 

print 'LOADED FEATS'
for nsamp in nsamp_list:
    for mode in ['train', 'test']:
        feats = allfeats[nsamp][mode]
        print 'NSAMP={0}, MODE={1}, ndocs={2}'.format(nsamp, mode, len(feats))
        output_file = 'feats/{ns}_{md}'.format(ns=nsamp, md=mode)
        go_feathash(feats, output_file, max_feats=MAX_FEATS)