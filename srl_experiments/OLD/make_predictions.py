from __future__ import division
import json
from collections import defaultdict, Counter
import numpy as np
#import ipdb

def get_mean_acc(nsamp, blacklist = set()):
    predicate2numcorrect = defaultdict(int)
    predicate2total = defaultdict(int)

    #load training examples 
    stem = 'train_nsamp'+str(nsamp)
    fin = 'feats/'+stem + '_feats.json'
    train_pred2feat = json.load(open(fin, 'r'))
    print len(train_pred2feat.keys())

    #testing 
    for line in open('feats/test_nsamp'+str(nsamp)+'_feats.json', 'r'):
        dd = json.loads(line)
        predicate = dd.keys()[0]

        if predicate in blacklist: continue #don't look at the predicates that for example have only been seen once in the training set! 
        if predicate not in train_pred2feat.keys(): continue #predicate in the test set that was never seen at training
        
        feats = dd.values()[0]
        
        #sort the argument propositions 
        arg2deps = defaultdict(list)
        for feat, weight in feats.iteritems():
            ss = feat.split('>')
            dlabel = ss[0]
            true_arg = ss[1]
            arg2deps[true_arg].append((dlabel, weight))

        if len(arg2deps) < 2 : continue #ignore predicates that do not have at least two arguments!!

        #TODO: I don't think this is the correct metric either b/c it gives unfair advantage to assigning all 0?? 
        argpred_all = {'arg'+str(k):0 for k in xrange(5)}
        argtrue_all = argpred_all.copy()
        
        #now find the soft probs for each arg  
        for arg_true, arg_feats in arg2deps.iteritems():
            arg_predict2prob = {}
            argtrue_all[arg_true] = 1 
            #for k in xrange(5): #iterate through all the predicted labels
            for k in xrange(5):
                prob = 0 
                for arg_feat in arg_feats:
                    deplabel, weight = arg_feat
                    proposed = deplabel+'>'+'arg'+str(k)
                    if proposed not in train_pred2feat[predicate].keys(): continue #we never saw this deplabel with this arg in the training set 
                    
                    prob += weight * train_pred2feat[predicate][proposed]
                arg_predict2prob['arg'+str(k)] = prob
        
            #now make a hard prediction which arg this should be!
            sorted_probs = sorted(arg_predict2prob.items(), key=lambda (k, v): -v)
            arg_pred, predict_prob = sorted_probs[0]
            argpred_all[arg_pred] = 1 

        if argpred_all == argtrue_all: predicate2numcorrect[predicate] +=1
        else:  predicate2numcorrect[predicate] += 0 #need this so that it records num correct as well! 
        predicate2total[predicate] += 1

    #do analysis of how accuracy; over all predicates; broken down by predicates?? 
    tc = sum(predicate2numcorrect.values())
    tseen = sum(predicate2total.values())
    print 'TOTAL CORRECT=', tc
    print 'TOTAL SEEN=', tseen
    print 'OVERALL ACC=', tc/tseen
    predicate2acc = {}
    for pred, numcor in predicate2numcorrect.iteritems():
        ttl = predicate2total[pred]
        if ttl == 0: acc = 0 
        else: acc = numcor / ttl
        predicate2acc[pred] = acc

    #get mean accuracy 
    mean_acc = np.mean(np.array(predicate2acc.values()))
    print len(predicate2numcorrect)
    print len(predicate2total)
    #ipdb.set_trace()
    return mean_acc

def thresh_pred(min_exs, pred2numexs):
    #threshold the predicates
    blacklist = set()
    for predicate, numexs in pred2numexs.iteritems():
        if numexs < min_exs: 
            blacklist.add(predicate)

    return blacklist

def main():
    MIN_EXS = 1

    #load the pred2numexs (here this will be the same for 10 and 100 samples and greedy, doesn't depend on the num of samples)
    fin = 'feats/train_nsamp10_pred2numexs.json'
    pred2numexs = json.load(open(fin, 'r'))

    blacklist = thresh_pred(MIN_EXS, pred2numexs)
    print 'num predicates <{0} exs ={1}'.format(MIN_EXS, len(blacklist))

    for nsamp in [1, 10, 100]:
        if nsamp == 1: print 'NUM_SAMP=', 'GREEDY' 
        else: print 'NUM_SAMP=', nsamp
        mean_acc = get_mean_acc(nsamp, blacklist=blacklist)
        print 'MEAN_ACC (mean over predicate acc)=', mean_acc
        print ''

if __name__ == "__main__": main()




