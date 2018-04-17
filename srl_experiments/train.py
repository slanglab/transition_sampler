from __future__ import division
import numpy as np
import sys,json,itertools,re,argparse
from collections import Counter,defaultdict
from get_feats import * 

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("nsamps", help="number of samples 10 or 100", type=str)
    args = parser.parse_args()

    num_samps = args.nsamps
    mode = 'train'
    print 'TRAINING w/ NSAMPS=', num_samps 

    #load the predicate-argument SRL stuff that has been processed from the Ontonotes dataset 
    predargs_file = 'data/{0}.json'.format(mode)
    predargs_list = [json.loads(line) for line in open(predargs_file, 'r')]
    parse_file = str(num_samps)+'samp_batches/'+mode+'_all.pred'
    
    #giant matrix that stores the counts of all these things 
    pred2feat2arg2count = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))
    pred2arg2numheads = defaultdict(lambda : defaultdict(int))
   
    #greedy need to divide by 1 later on! 
    if num_samps == 'greedy': num_samps = 1 
    else: num_samps = int(num_samps)

    if mode == 'train':
        for sentnum, parse in enumerate(yield_conll_sentences(open(parse_file))):
            predargs = predargs_list[sentnum]
            assert len(parse['words']) - 1 == len(predargs['toks']), 'Error! Parses and pred-arg examples could be misaligned'
            #need the -1 because we add on the root for the dependencies 

            #skip examples that do not have a predicate, argument 
            if len(predargs['pred_args']) == 0: continue 

            for pred_arg in predargs['pred_args']:
                pred2feat2arg2count, pred2arg2numheads = get_feats_1predicate(pred_arg, parse['parse_samples'], pred2feat2arg2count, pred2arg2numheads)
                             
        #dump here
        stem = mode + '_nsamp'+str(num_samps)
        fout1 = 'feats/'+stem + '_feats.json'
        ww = open(fout1, 'w')
        json.dump(pred2feat2arg2count, ww)
        ww.close()
        print 'WROTE TO: ', fout1 

        #dump here
        fout1 = 'feats/'+stem + '_numheads.json'
        ww = open(fout1, 'w')
        json.dump(pred2arg2numheads, ww)
        ww.close()
        print 'WROTE TO: ', fout1 

if __name__ == "__main__": main()