from __future__ import division
import numpy as np
import sys,json,itertools,re,argparse
from collections import Counter,defaultdict
from get_feats import *


parser = argparse.ArgumentParser()
parser.add_argument("nsamps", help="number of samples 10 or 100", type=str)
args = parser.parse_args()
num_samps = args.nsamps
mode = 'test'
print 'TESTING w/ NSAMPS=', num_samps 

test_pred2numcorrect = defaultdict(int)
test_pred2total = defaultdict(int)

#load the predicate-argument SRL stuff that has been processed from the Ontonotes dataset 
predargs_file = 'data/{0}.json'.format(mode)
predargs_list = [json.loads(line) for line in open(predargs_file, 'r')]

parse_file = str(num_samps)+'samp_batches/'+mode+'_all.pred'

#greedy need to divide by 1 later on! 
if num_samps == 'greedy': num_samps = 1 
else: num_samps = int(num_samps)

#load training examples 
stem = 'train_nsamp'+str(num_samps)
fin = 'feats/'+stem + '_feats.json'
train_pred2feat2arg2count = json.load(open(fin, 'r'))

def get_true_argspans(pred_arg):
    true_args = []
    for k, v in pred_arg.iteritems():
        if k not in ['arg0', 'arg1', 'arg2', 'arg3', 'arg4']: continue 
        if v[0] == '-': continue 
        true_args.append((k, v))
    return true_args 

#FIND THE ACCURACIES! 
for sentnum, parse in enumerate(yield_conll_sentences(open(parse_file))):
    predargs = predargs_list[sentnum]
    assert len(parse['words']) - 1 == len(predargs['toks']), 'Error! Parses and pred-arg examples could be misaligned'
    #need the -1 because we add on the root for the dependencies 

    #skip examples that do not have a predicate, argument 
    if len(predargs['pred_args']) == 0: continue
        
    for pred_arg in predargs['pred_args']:
        predicate = unicode((pred_arg['pred_lemma'], pred_arg['pred_framesetID']))
        pred_idx = int(pred_arg['pred_idx'])
        
        #skip examples in training that do not occur in testing
        if predicate not in train_pred2feat2arg2count.keys(): continue
            
        #iterate thru all the true argspans
        for arg_true, argspan in get_true_argspans(pred_arg):
            arg_prop2prob = {'arg'+str(k): 0 for k in xrange(5)}
            #iterate thru all the samples

            seen_parse_and_feat = 0 #make sure we normalize by the number of parse samples actualy seen
            for parse_samp, times_parse_seen in parse['parse_samples'].iteritems(): 
                #get the feature out 
                feat, _ = get_feats_1samp_1arg(parse_samp, argspan, pred_idx)

                if feat not in train_pred2feat2arg2count[predicate].keys(): continue #never saw that feature with that predicate
                seen_parse_and_feat += times_parse_seen

                #iterate through the possible arguments, find their probabilites in the training data given that feat! 
                c_all = []
                for l in xrange(5):
                    if 'arg'+str(l) not in train_pred2feat2arg2count[predicate][feat].keys(): 
                        c_all.append(0)
                    else: 
                        c_all.append(train_pred2feat2arg2count[predicate][feat]['arg'+str(l)])
                    c_denom = sum(c_all)

                #then calculate them 
                for k in xrange(5):
                    c_num = c_all[k]
                    arg_prop2prob['arg'+str(k)] += (c_num/c_denom) * times_parse_seen

            #normalize the predictions
            if seen_parse_and_feat == 0: continue #did not see any of the features for that parse sample
            arg_prop2prob_norm = {}
            for k, v in arg_prop2prob.iteritems():
                arg_prop2prob_norm[k] = v / seen_parse_and_feat

            #then make predictions! 
            sorted_probs = sorted(arg_prop2prob_norm.items(), key=lambda (k, v): -v)
            arg_pred, predict_prob = sorted_probs[0]
            
            if arg_pred == arg_true: test_pred2numcorrect[predicate] += 1 
            test_pred2total[predicate] += 1

#then calculate per-predicate accuracy 
test_pred2acc = {}
for predicate, numcorr in test_pred2numcorrect.iteritems():
    test_pred2acc[predicate] = numcorr / test_pred2total[predicate]

stem = mode + '_nsamp'+str(num_samps)
fout1 = 'accs/'+stem + '_accs.json'
ww = open(fout1, 'w')
json.dump(test_pred2acc, ww)
ww.close()
print 'WROTE TO: ', fout1 
