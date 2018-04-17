from __future__ import division
import numpy as np
import sys,json,itertools,re,argparse
from collections import Counter,defaultdict
from extrfeats import *


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
        #sent['lemmas'] = [x['lemma'] for x in sent['tokens']]
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

def go_extr_feats(filename, output_file, num_samp):
    #only extracts dependency features
    #modified from extrfeats.extr_all_feats
    allfeats = []
    doc_count = 0 
    zero_feats = 0
    SYMBOLS = set(["TARGET", "PERSON"])

    for sent in yield_conll_sentences(open(filename)):
        doc_count += 1
        print doc_count
        feats = defaultdict(float)
        tokens=[w.lower() if w not in SYMBOLS else w for w in sent['words']]

        if 'TARGET' not in tokens: #arg still have bad files that don't work here..
            zero_feats +=1
            allfeats.append(feats)
            continue
        pos_tags = sent['pos']
        targ_idxs =[i for i, x in enumerate(tokens) if x == 'TARGET'] #there can be multiple TARGETS in a sentence
        tok_idxs = [i for i in range(len(tokens))]

        #then go thru each dependency sample
        for deps, count in sent['parse_samples'].iteritems():
            deps = json.loads(deps) #switch back from string into list
            edges, direc = get_edges_dir(deps)
            for path in get_paths_incl_targ(edges, targ_idxs):
                feats[b1(path, tokens, direc, pos_tags)] += 1.0 * count / num_samp
                feats[b2(path, tokens, direc)] += 1.0 * count / num_samp
                feats[b3(path, tokens, pos_tags)] += 1.0 * count / num_samp
            #getting b4 feats
            for path in get_len_2(direc):
                feats[b1(path, tokens, direc, pos_tags)] += 1.0 * count / num_samp

        if len(feats) == 0: zero_feats+= 1
        allfeats.append(feats)

    assert len(allfeats) == doc_count
    print 'len allfeats=', len(allfeats)
    print "READ {0} DOCS FROM FILE {1}".format(doc_count, filename)
    print "NUM DOCS WITH ZERO FEATS=",zero_feats
    w = open(output_file, 'w')
    json.dump(allfeats, w)
    print 'wrote allfeats to ', output_file
    return allfeats

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="e.g. ", type=str)
    parser.add_argument("nsamp", help="number of samples (10 or 100)", type=int)
    parser.add_argument("--greedy", action='store_true', help="greedy flag to save to different folder")
    args = parser.parse_args()

    if not args.greedy:  
        sout = args.input.split('/')
        output_file = 'feats_'+sout[-2]+'/'+sout[-1]+'.feats'
    else: 
        sout = args.input.split('/')
        output_file = 'feats_batches_greedy/'+sout[-1]+'.feats'

    #output_file = 'feats_toy/'+args.input
    go_extr_feats(args.input, output_file, args.nsamp)

if __name__ == "__main__":
    main()


