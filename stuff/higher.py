"""
Internally there are two different data formats for paths.
One is the "pathy" form of a path that has a notion of traversal order:
    (3, "UP", "nsubj", 7, "DOWN", "dobj", 13)
It always starts and ends with a word.  This is convenient for the recursive
path-extension algorithm to enumerate paths.  (Is there a different algorithm
that would be better to use?)

The second format is sometimes called "edgeset" to distinguish versus a pathy
path, though outside of the core path code, it's sometimes just called a path:
    set([ ("nsubj",7,3), ("dobj",7,13) ])
This is just a set of tuples, and each tuple is a fully specified labeled edge.
It's a subgraph without any ordering information.
"""
from __future__ import division
from pprint import pprint
from collections import Counter,defaultdict,namedtuple
import math,sys,termcolor

def yield_sentences():
    L1=[]; L2=[]
    for line1,line2 in zip(open(f1),open(f2)):
        if not line1.strip():
            yield L1,L2
            L1=[]; L2=[]
            continue
        L1.append(line1); L2.append(line2)
    if L1 or L2: yield L1,L2

def entropy(countdict):
    tot = sum(countdict.itervalues())
    ent = 0.0
    for k,n in countdict.iteritems():
        p = n/tot
        ent += -p*math.log(p) if p>0 else 0
    return ent

NextEdge = namedtuple('NextEdge', 'dir rel nextind')

def make_index(deps):
    """deps: a list of (rel,gov,child) tuples."""
    d = {}
    d['node2edges'] = defaultdict(list)
    for rel,gov,child in deps:
        d['node2edges'][child].append( NextEdge("UP",rel,nextind=gov) )
        d['node2edges'][gov].append( NextEdge("DOWN",rel,nextind=child) )
    return d

def extend_paths(index,paths):
    """paths: a set/sequence of "pathy" paths"""
    for path in paths:
        lastind = path[-1]
        seen = set(path)  # actually we only care about getting token indices into this set
        for edge in index['node2edges'].get(lastind,[]):
            if edge.nextind in seen: continue
            if edge.rel in BLACKLIST: continue
            yield path + (edge.dir,edge.rel,edge.nextind)

# BLACKLIST = set(['punct'])
BLACKLIST = set()
print "EDGE BLACKLIST", BLACKLIST

def get_paths_len1(index,Ntok):
    """Returns edgesets."""
    allpaths = set()
    for i in xrange(1,Ntok+1):
        i=str(i)
        tokpaths_len1 = set(extend_paths(index, [(i,)] ))
        allpaths |= tokpaths_len1
    return set(path_to_edgeset(path) for path in allpaths)

def get_paths_len2(index, Ntok):
    """Returns edgesets."""
    allpaths = set()
    for i in xrange(1,Ntok+1):
        i=str(i)
        tokpaths_len1 = list(extend_paths(index, [(i,)] ))
        tokpaths_len2 = set()
        for pp in extend_paths(index, tokpaths_len1):
            tokpaths_len2.add(pp)
        allpaths |= tokpaths_len2
    return set(path_to_edgeset(path) for path in allpaths)

def get_paths_with_len(index, Ntok, target_length=3):
    """Generalizes the prev two functions.  Returns edgesets."""
    def tokpaths(i):
        # paths starting at i
        i=str(i)
        curpaths = set(extend_paths(index, [(i,)] ))
        for length in xrange(2, target_length+1):
            newpaths = set(extend_paths(index, curpaths))
            curpaths = newpaths
        return curpaths
    def allpaths():
        for i in xrange(1,Ntok+1):
            for path in tokpaths(i):
                yield path
    return set(path_to_edgeset(path) for path in allpaths())


def path_to_edgeset(path):
    # print
    # print path
    edges = []
    curind = path[0]
    for j in xrange(1,len(path),3):
        dir,rel,nextind = path[j:j+3]
        # print dir,rel,nextind
        newedge =   (rel,curind,nextind) if dir=='DOWN' else \
                    (rel,nextind,curind) if dir=='UP' else \
                    None
        assert newedge is not None
        edges.append(newedge)
        curind = nextind
    # print edges
    return frozenset(edges)

def nicepath(tokens, edgeset):
    # would be better to take the pathy format to have original path order
    edgeset = [(rel,int(gov),int(child)) for rel,gov,child in edgeset]
    edgeset.sort(key=lambda (r,g,c): (c,g,r))
    out=[]
    # print tokens
    for rel,gi,ci in edgeset:
        # print rel,gi,ci
        out.append(u"{rel}({gw}:{gi}, {cw}:{ci})".format(rel=rel,
            ci=ci,gi=gi,
            gw=tokens[gi],
            cw=tokens[ci]))
    return u"[%s]" % u", ".join(out)


import argparse
pp = argparse.ArgumentParser()
pp.add_argument('goldfile')
pp.add_argument('predfile')
pp.add_argument('--greedy',  action='store_true')
pp.add_argument('--edgepred',  action='store_true')
pp.add_argument('--treepred',  action='store_true')
pp.add_argument('--verbose','-v',action='store_true')
pp.add_argument('--tlen', type=int)
pp.add_argument('--numsent', type=int)
args = pp.parse_args()
# print args;sys.exit()

f1,f2 = args.goldfile, args.predfile


tp,fp,fn = 0,0,0

# get_paths = get_paths_len2
# get_paths = get_paths_len1
get_paths = lambda *aa: get_paths_with_len(*aa, target_length=args.tlen)

for sentnum,(lines1,lines2) in enumerate(yield_sentences()):
    if sentnum%100==0: sys.stderr.write(".")
    Ntoken = len(lines1)
    # if not (15 <= Ntoken <= 15): continue
    # if Ntoken !=10: continue
    tokens = ["ROOT"]+[line1.split()[1] for line1 in lines1]

    gold_edges = []
    for line1,line2 in zip(lines1,lines2):
        goldparts = line1.strip().split("\t")
        predparts = line2.strip().split("\t")
        assert predparts[0:2]==goldparts[0:2]
        goldparts = line1.strip().split("\t")
        child,goldgov,goldrel = goldparts[0],goldparts[6],goldparts[7]
        gold_edges.append( (goldrel,goldgov,child) )

    if not args.greedy:
        fulltree_samples = defaultdict(list)
        for line2 in lines2:
            predparts = line2.strip().split("\t")
            tokind = predparts[0]
            arc_samples = [x.split() for x in predparts[6:]]
            arc_samples = [(gov,rel) for gov,rel in arc_samples]
            for sampleind,(gov,rel) in enumerate(arc_samples):
                fulltree_samples[sampleind].append( (rel,gov,tokind) )
        fulltree_samples = fulltree_samples.values()
    elif args.greedy:
        greedy_pred_edges = []
        for line2 in lines2:
            predparts = line2.strip().split("\t")
            child,predgov,predrel = predparts[0],predparts[6],predparts[7]
            greedy_pred_edges.append( (predrel,predgov,child) )
        fulltree_samples = [ greedy_pred_edges ]  # a 'sample'

    treedist = Counter(frozenset(x) for x in fulltree_samples)
    if args.verbose:
        print "\nSENTENCE\t%s" % (" ".join( line1.split()[1] for line1 in lines1 ))
        print "length %3s support size %3d entropy %.3f topprob %s"  % (
                Ntoken,
                len(treedist), 
                entropy(treedist),
                [n for (_,n) in treedist.most_common(5)],
        )

    gold_ix = make_index(gold_edges)
    gold_paths = get_paths(gold_ix, Ntoken)
    print "%d gold paths" % (len(gold_paths))

    ## single prediction higher order analysis
    if args.treepred:
        tt = treedist.most_common(1)[0][0]
        pred_ix = make_index(tt)
        pred_paths = get_paths(pred_ix,Ntoken)
        Ngold = len(gold_paths)
        Npred = len(pred_paths)
        Nboth = len(gold_paths & pred_paths)
        prec=Nboth/Npred if Nboth else 0; rec=Nboth/Ngold if Nboth else 0
        # print "gold %s, pred %s, both %s, prec %.3f, rec %.3f, f %.3f" % (
        #         Ngold,Npred,Nboth, prec,rec, 0 if Nboth==0 else 2*prec*rec/(prec+rec))
        tp += Nboth
        fp += len(pred_paths - gold_paths)
        fn += len(gold_paths - pred_paths)

    ## higher order MBR
    if args.edgepred:
        path_marginals = defaultdict(float)
        Z = sum(treedist.values())
        # assert Z==1000
        for tt,weight in treedist.items():
            pred_ix = make_index(tt)
            pred_paths = get_paths(pred_ix,Ntoken)
            for path in pred_paths:
                path_marginals[path] += weight/Z
        print "%d gold paths, %d pred paths support, %d intersection" % (len(gold_paths), len(path_marginals), len( set(gold_paths) & set(path_marginals) ))
        allpaths = set(gold_paths) | set(path_marginals)
        allpaths = sorted(allpaths, key=lambda path: -path_marginals.get(path,0))

        for path in allpaths:
            is_gold = int(path in gold_paths)
            predprob = path_marginals.get(path,0)
            print "EDGEPRED",predprob,is_gold, "AAA", nicepath(tokens, path)
            ## expected recall,prec is wonky
            # if is_gold:
            #     tp += predprob
            #     fn = (1-predprob)
            # else:
            #     fp += predprob

    # sys.exit()
    if args.numsent is not None and sentnum+1 >= args.numsent: break

print "num sentences:", sentnum+1

prec=tp/(tp+fp) if tp+fp else 0
rec =tp/(tp+fn) if tp+fn else 0
print "final tp %s fp %s fn %s" % (tp,fp,fn)
print "final prec %.3f rec %.3f f %.3f" % (prec,rec, 2*prec*rec/(prec+rec) if prec+rec else 0)
