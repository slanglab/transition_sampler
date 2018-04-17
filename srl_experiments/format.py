from __future__ import division
import json
#import ipdb 

#the column headers from "saved_cemantix.org_data_ontonotes.txt"
clmn2header ={
    0: "docid",
    1: "part_number",
    2: "word_idx",
    3: "word_token",
    4: "pos",
    5: "const_parse",
    6: "pred_lemma",
    7: "pred_framesetID",
    8: "word_sense",
    9: "speaker",
    10: "named_ents",
    11: "pred_args" #this is really 12:N (depending on the number of args there are)
}
#N = coreference chain 
header2clmn = {v:k for k, v in clmn2header.iteritems()}

predargs_template = {'pred_idx': 0, 'pred_lemma': '', 'arg0' : ['-', '-'], 'arg1': ['-', '-'], 'arg2': ['-', '-'], 'arg3': ['-', '-'], 'arg4': ['-', '-']}
sent_template = {'docid': '', 'sentid': 0, 'toks': [], 'pos': [], 'pred_args': []}

START_ARGS = ['(ARG0*', '(ARG1*', '(ARG2*', '(ARG3*', '(ARG4*']
START_END_ARGS = ['(ARG0*)', '(ARG1*)', '(ARG2*)', '(ARG3*)', '(ARG4*)']
start2norm = {'(ARG0*': 'arg0', '(ARG1*': 'arg1', '(ARG2*': 'arg2', '(ARG3*': 'arg3', '(ARG4*': 'arg4',
            '(ARG0*)': 'arg0', '(ARG1*)': 'arg1', '(ARG2*)': 'arg2', '(ARG3*)': 'arg3', '(ARG4*)': 'arg4'}

#for ff in ['data/train.txt', 'data/development.txt', 'data/test.txt']:
#for ff in ['data/test.txt']:
for ff in ['data/toy1.txt']:
    ww = open(ff.split('.')[0]+ '.json', 'w')
    ww_sents = open(ff.split('.')[0]+ '_sents'+'.txt', 'w')

    sent_num = 0
    for line_num, line in enumerate(open(ff, 'r')):
        print line_num, ff
        tabs = line.rstrip().split()
        if len(tabs) == 0:
            # if len(sent_obj['pred_args']) != 0: 
            #     print sent_obj['pred_args'] 
            #     ipdb.set_trace() 
            #end of sentence 
            #write current sentence to file
            assert len(toks) == len(pos)
            sent_obj['toks'] = toks
            sent_obj['pos'] = pos
            print sent_obj
            json.dump(sent_obj, ww)
            ww.write('\n')
            
            #write sent text
            sent_text = str(' '.join(toks))
            print sent_text
            print 
            ww_sents.write(sent_text+'\n')
            sent_num+= 1
            continue

        if tabs[0] in ['#begin','#end']: continue #begin or end of the document

        if int(tabs[header2clmn['word_idx']]) == 0: 
            #new sentence 
            print 'NEW SENTENCE'
            num_preds = len(tabs)-12 #number of predictates 
            toks = []
            pos = []
            sent_template = {'docid': '', 'sentid': 0, 'toks': [], 'pos': [], 'pred_args': []}
            sent_obj = sent_template.copy()
            predargs_template = {'pred_idx': 0, 'pred_lemma': '', 'arg0' : ['-', '-'], 'arg1': ['-', '-'], 'arg2': ['-', '-'], 'arg3': ['-', '-'], 'arg4': ['-', '-']}
            sent_obj['pred_args'] = [predargs_template.copy() for p in xrange(num_preds)]
            sent_obj['docid'] = tabs[header2clmn['docid']]
            sent_obj['sentid'] = sent_num
            current_arg = [None for p in xrange(num_preds)]
        
        #then each row is a different token
        toks.append(tabs[header2clmn['word_token']])
        pos.append(tabs[header2clmn['pos']])
        
        for pp in xrange(num_preds):
            #check to see if there's a start idx 
            possible_arg = tabs[header2clmn['pred_args'] + pp]
            #print 'pp=', pp, 'idx=', tabs[header2clmn['word_idx']], possible_arg, current_arg
            # print possible_arg
            # print sent_obj['pred_args']
            # print ''
 
            #continue 
            if possible_arg == '*': continue 

            #starting and ending argument span
            elif possible_arg in START_END_ARGS:
                arg = start2norm[possible_arg]
                #assign both the start and end token to that same argument 
                #shouldn't need a current_arg since it's already over 
                sent_obj['pred_args'][pp][arg][0] = tabs[header2clmn['word_idx']]
                sent_obj['pred_args'][pp][arg][1] = tabs[header2clmn['word_idx']] 
            
            #starting an argument span
            elif possible_arg in START_ARGS:
                arg = start2norm[possible_arg]
                current_arg[pp] = arg
                sent_obj['pred_args'][pp][arg][0] = tabs[header2clmn['word_idx']]
            
            #ending an agrument span 
            elif possible_arg == '*)': 
                arg = current_arg[pp]
                if arg == None: continue #this could happen in cases when we have an adjunct first like "head -92719 data/train.txt| tail -1"
                sent_obj['pred_args'][pp][arg][1] = tabs[header2clmn['word_idx']]
                current_arg[pp] = None 
                
            #verb predicate
            elif possible_arg == '(V*)':
                sent_obj['pred_args'][pp]['pred_idx'] = tabs[header2clmn['word_idx']]
                sent_obj['pred_args'][pp]['pred_lemma'] = tabs[header2clmn['pred_lemma']]


