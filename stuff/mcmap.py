"""
do the stupid "mc-map" algorithm. 
input: our sample format
output: conll single-parse format, i guess
"""


from __future__ import division
from pprint import pprint
from collections import Counter,defaultdict,namedtuple
import math,sys,termcolor

def yield_sentences():
    L1=[]
    for line1 in sys.stdin:
        if not line1.strip():
            yield L1
            L1=[]
            continue
        L1.append(line1)
    if L1: yield L1

def entropy(countdict):
    tot = sum(countdict.itervalues())
    ent = 0.0
    for k,n in countdict.iteritems():
        p = n/tot
        ent += -p*math.log(p) if p>0 else 0
    return ent

import argparse
pp = argparse.ArgumentParser()
pp.add_argument('--verbose','-v',action='store_true')
args = pp.parse_args()

for sentnum,lines1 in enumerate(yield_sentences()):
    if sentnum%100==0: sys.stderr.write(".")
    Ntoken = len(lines1)
    # if not (15 <= Ntoken <= 15): continue
    # if Ntoken !=10: continue
    tokens = ["ROOT"]+[line.split()[1] for line in lines1]

    fulltree_samples = defaultdict(list)
    for line in lines1:
        predparts = line.strip().split("\t")
        tokind = predparts[0]
        arc_samples = [x.split() for x in predparts[6:]]
        arc_samples = [(gov,rel) for gov,rel in arc_samples]
        for sampleind,(gov,rel) in enumerate(arc_samples):
            fulltree_samples[sampleind].append( (rel,gov,tokind) )
    fulltree_samples = fulltree_samples.values()

    treedist = Counter(frozenset(x) for x in fulltree_samples)
    if args.verbose:
        print "\nSENTENCE\t%s" % (" ".join( line.split()[1] for line in lines1 ))
        print "length %3s support size %3d entropy %.3f topprob %s"  % (
                Ntoken,
                len(treedist), 
                entropy(treedist),
                [n for (_,n) in treedist.most_common(5)],
        )

    top_parse= treedist.most_common(1)[0][0]
    childs = [c for (r,g,c) in top_parse]
    assert len(childs)==len(set(childs))
    child2rg = {c: (r,g) for (r,g,c) in top_parse}
    for line in lines1:
        predparts = line.strip().split("\t")
        out = ['']*10
        out[:6] = predparts[:6]
        tokind = predparts[0]
        r,g = child2rg[tokind]
        out[6] = g
        out[7] = r
        out[8] = "_"
        out[9] = "_"
        print '\t'.join(out)
    print
        

