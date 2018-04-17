from __future__ import division
import numpy as np
import sys,json,itertools,re,argparse
from collections import Counter,defaultdict
#import ipdb

'''
NOTES! the really confusing thing here is that the indexes for the parse sample
and the idexes for the predicate-argument span are off by one b/c 
the parse samples have this ROOT node up front!! 
'''


#taken from ../pfrules.py
#but modified so that it returns the parse_samples as a dictionary of counts,
#so don't have to run thru them all 
def yield_conll_sentences(infile_pointer):
    have_printed_info = False
    def yield_lines():
        L1=[]
        for line1 in infile_pointer:
            if not line1.strip():
                yield L1
                L1=[]
                continue
            L1.append(line1)
        if L1: yield L1

    for lines in yield_lines():
        # make similar to decorate_corenlp() output
        sent = {}
        lines = [line.decode("utf8") for line in lines]
        rows = [line.rstrip("\n").split("\t") for line in lines]
        sent['tokens'] = [{'pos':row[4], 'lemma':row[2], 'word':row[1]} for row in rows]
        sent['tokens'] = [{'pos':'ROOT', 'lemma':'ROOT', 'word':'ROOT'}] + sent['tokens']
        sent['words'] = [x['word'] for x in sent['tokens']]
        sent['pos'] = [x['pos'] for x in sent['tokens']]
        sent['lemmas'] = [x['lemma'] for x in sent['tokens']]
        # assert False, "todo"
        parse_samples = defaultdict(int)

        traditional_conll_format = len(rows[0][6].split())==1
        if traditional_conll_format:
            triples = [(row[7],row[6],row[0]) for row in rows]
            triples = [(r, int(g), int(c)) for (r,g,c) in triples]
            parse_samples[json.dumps(triples)] += 1  ## only one 'sample'
        else:
            # our 'sample column' format
            first_samples = [x for x in rows[0][6:] if x.strip()]
            Nsample = len(first_samples)
            if not have_printed_info:
                print>>sys.stderr, "detected %s samples" % Nsample
                have_printed_info = True

            for sample_num in xrange(Nsample):
                j = 6+sample_num
                # govarcs = [row[6+sample_num] for row in rows]
                triples = [ (row[j].split()[1], int(row[j].split()[0]), int(row[0])) for row in rows]
                # print "SAMPLE",triples
                parse_samples[json.dumps(triples)] += 1
        sent['parse_samples'] = parse_samples
        yield sent



def get_head(parse_samp, argspan):
    '''
    parse_samp::
    a single parse edges example e.g.
    parse_samp = [['deplabel', 4, 2], ['deplabel', 2, 3], ['deplable', 3, 1]]
    
    argspan::
    the starting and ending tokens for a single argument 
    argspan =[u'0', u'2']
    
    this returns the "head index" from the argspan
    by using the dependency edges given by parse_samp 
    '''
    votes = defaultdict(int)
    child2parent = {(edge[2]-1):(edge[1]-1) for edge in parse_samp} #need the -1 for parse to argspan aligning
    assert len(child2parent) == len(parse_samp), 'problem with parse tree structure??'
    
    as_start = int(argspan[0]) #starting index of argument text span
    as_end = int(argspan[1]) #ending index of argument text span 
    arg_tokrange =[x for x in xrange(as_start, as_end+1)]
     
    #make votes by iterating thru all the toks 
    for tok in arg_tokrange:
        #basecase tok is the head 
        child = tok 
        parent = child2parent[child]
        #go up the paths until you EXIT the token span of the current argument 
        while parent in arg_tokrange:
            child = parent
            parent = child2parent[child]
        head = child
        votes[head] += 1
    
    #then find the head index
    max_votes = max(votes.values())
    possible_heads = [k for k in votes.keys() if votes[k] == max_votes]
    head_idx = min(possible_heads) #IMPORTANT: ties go to the smallest index 
    
    return head_idx, len(possible_heads)

def get_feats_1samp_1arg(parse_samp, argspan, pred_idx):
    '''
    for one parse sample and one argument, find the length one dependency edge between the 
    predicate and the head of the argument 
    '''
    head_idx, num_possible_heads = get_head(json.loads(parse_samp), argspan)

    #now see if there's an edge between predicate and argument head 
    for edge in json.loads(parse_samp):
        deplabel = str(edge[0])
        parent = int(edge[1]) -1 
        child = int(edge[2])-1 

        if parent == pred_idx and child == head_idx: 
            return deplabel + '_DOWN', num_possible_heads #going down from predicate to arg head 

        elif parent == head_idx and child == pred_idx:
            return deplabel + '_UP', num_possible_heads # going up from the arg head to the predicate 

    return '<NO_EDGE_FOUND>', num_possible_heads

def get_feats_1predicate(pred_arg, parse_samples, feats, pred2arg2numheads):
    '''
    for one predicate (in one example) and an arbitrary number of parse samples, find all those features 
    '''
    pred_idx = int(pred_arg['pred_idx'])
    predicate = (pred_arg['pred_lemma'], pred_arg['pred_framesetID'])

    for sample, weight in parse_samples.iteritems(): 
        for k in xrange(5):

            #TODO: count how many times the headword changes?? 
            arg = 'arg'+str(k)
            argspan = pred_arg[arg]
            if argspan[0] == '-': continue #no arguments here 
            feat_1samp, num_possible_heads = get_feats_1samp_1arg(sample, argspan, pred_idx)
            pred2arg2numheads[str(predicate)][str(arg)] += num_possible_heads
            feats[str(predicate)][str(feat_1samp)][str(arg)] += weight 

    return feats, pred2arg2numheads 



