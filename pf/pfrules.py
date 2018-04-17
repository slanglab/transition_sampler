"""
derived from an.py with changes
 - runs on samples
"""
from __future__ import division
import numpy as np
import sys,json,itertools,re
from collections import Counter,defaultdict

REPO = "/home/brenocon/newsevents"
KILL = set(L.strip() for L in open("{REPO}/gnews_scraper/kill_keywords.txt".format(**locals())) if L.strip())
POLICE = set(L.strip() for L in open("{REPO}/gnews_scraper/police_keywords.txt".format(**locals())) if L.strip())
# print KILL
# print POLICE

# the ':' things are sometimes only in the 'enhanced' deps. these rules havent
# been properly adapted to basic-only deps.
REL_NORM_TABLE = {
    'amod': 'mymod',
    'compound': 'mymod',
    # 'nsubj:xsubj': 'mysubj',
    'nsubj': 'mysubj',
    'nmod:agent': 'mysubj',
    'nmod': 'mysubj',
    'nsubjpass': 'myobj',
    'dobj': 'myobj',
}
REL_NORM_TABLE = {unicode(k):unicode(v) for k,v in REL_NORM_TABLE.items()}

REL_BLACKLIST = set(['case','mark','punct','det','aux','auxpass','acl:relcl'])

def rel_normalize(dep_triples):
    def gen(xx):
        for (r,g,c) in xx:
            if r in REL_BLACKLIST:
                continue
            if r.startswith('conj'):
                continue
            if r in REL_NORM_TABLE:
                yield (REL_NORM_TABLE[r], g,c)
            elif r=='appos':
                yield ('mymod',g,c)
                yield ('mymod',c,g)
            else:
                yield (r,g,c)
    xx = gen(dep_triples)
    return list(xx)

def check_sentence(sent):
    N = len(sent['words'])
    tgts = [i for i in range(N) if sent['words'][i]=='TARGET']
    if not tgts: return False
    tgtind = tgts[0]
    # print sent['words']
    is_pol_word = [(w.lower() in POLICE) for w in sent['words']]
    is_kill_word = [(w.lower() in KILL) for w in sent['words']]
    # print sum(is_pol_word), is_pol_word
    # print sum(is_kill_word), is_kill_word
    # print sent['deps']

    # NOTE nmod:of never appears in basic UDs.
    cands = [(r,g) for (r,g,_) in sent['c2deps'][tgtind] \
            if is_kill_word[g] and (r=='myobj' or r=='nmod:of')]
    if not cands: return False
    print "KILLCANDS\t" + repr(cands)
    def is_pol_ent(i):
        return sent['tokens'][i]['pos'].startswith("NN") and \
                any(is_pol_word[m] for m in get_np_modifiers(sent,i))
    def final():
        for _,g in cands:
            subjs = [c for (r,_,c) in sent['g2deps'][g] if r=='mysubj' and is_pol_ent(c)]
            for subj in subjs:
                yield (subj,g)
    killing_tuples = list(final())
    print "TUPLES %s" % (len(killing_tuples))
    for subj,kill in killing_tuples:
        print "\t %s:%s <-- %s:%s" % (sent['words'][subj],subj, sent['words'][kill],kill)
    return bool(killing_tuples)


def gorules(conll_parse_file, Nsample, sentment_file=None):
    """sentment_file will be iterated through in parallel as the conll-formatted dep parse file."""
    Nsample=int(Nsample)
    sentment=None; sentment_fp=None
    sentment_fp = iter(open(sentment_file)) if sentment_file else None

    for sent_allparses in yield_conll_sentences(open(conll_parse_file)):
        if sentment_fp:
            sentment = sentment_fp.next()
            sentment = json.loads(sentment.split("\t")[0])
        # sent = create_sent_for_sample(sent_allparses, 0)
        # import viewdeps
        # viewdeps.viewdeps_govfirst(sent)
        # print repr(sent_allparses['words'])
        print "TEXT\t" + u" ".join(sent_allparses['words']).encode("utf8")
        assert Nsample <= len(sent_allparses['parse_samples'])
        Nmatch = 0
        for s in xrange(Nsample):
            sent = create_sent_for_sample(sent_allparses, s)
            Nmatch += int(check_sentence(sent))

        out = {}
        out['sent_alter'] = u" ".join(sent_allparses['words'][1:])

        if sentment:
            def wsnorm(x):
                return re.sub(r'\s+'," ",x).strip()
            assert wsnorm(out['sent_alter']) == wsnorm(sentment['sent_alter'])
            out.update(sentment)

        out['weight'] = Nmatch / Nsample
        if Nmatch>0:
            print "NONZERO"
        print "WEIGHT", out['weight']
        print "OUT\t" + json.dumps(out)

def get_np_modifiers(sent,tokind):
    # include itself
    return [tokind] + [c for (r,_,c) in sent['g2deps'][tokind] if r=='mymod']

def decorate_corenlp(sent):
    # adds extra datastructures to corenlp sentence dict
    sent['tokens'] = [{'pos':'ROOT', 'lemma':'ROOT', 'word':'ROOT'}] + sent['tokens']
    sent['words'] = [x['word'] for x in sent['tokens']]
    sent['lemmas'] = [x['lemma'] for x in sent['tokens']]

    deps = sent['enhancedPlusPlusDependencies']
    # deps = sent['basicDependencies']
    deps = [(x['dep'],x['governor'],x['dependent']) for x in deps]
    finalize_deps(sent, deps)

def create_sent_for_sample(sent_with_many_samples,samplenum):
    """create a new dummy sentence object whose parse is one of the parse samples."""
    newsent = dict(sent_with_many_samples)
    del newsent['parse_samples']
    finalize_deps(newsent, sent_with_many_samples['parse_samples'][samplenum])
    return newsent

def finalize_deps(sent, deps):
    """take 'deps' (list of (rel,gov,child) triples) as INPUT. MUTATE 'sent'."""
    deps = rel_normalize(deps)
    # Indexes for graph traversal
    g2deps,c2deps = defaultdict(list), defaultdict(list)
    for r,g,c in deps:
        g2deps[g].append((r,g,c))
        c2deps[c].append((r,g,c))
    N = len(sent['tokens'])
    sent['g2deps']={g:g2deps[g] for g in xrange(N)}
    sent['c2deps']={c:c2deps[c] for c in xrange(N)}
    sent['deps'] = deps

def sample_map():
    """stdin: parse sample file.  stdout: MAP single structure.  open question: is this same or diff than greedy?"""
    for sent in yield_conll_sentences(sys.stdin):
        parses = [tuple(x) for x in sent['parse_samples']]
        # print parses
        counts = Counter(parses)
        parse,count = counts.most_common(1)[0]
        for i in xrange(1,len(sent['words'])):
            pos = sent['tokens'][i]['pos']
            out = [str(i), sent['words'][i], "_", pos,pos, "_"]
            matches = [(g,r) for (r,g,c) in parse if c==i]
            assert len(matches)==1
            out.append("%s %s" % matches[0])
            print u"\t".join(out).encode("utf8")
        print

def yield_conll_sentences(infile_pointer):
    """
    iterate through conll-like parse sample sentences.
    the format from our hacked corenlp parser.
    where it's mostly conll, except a bunch of columns appended on the right
    side, where each column has one full parse.
    
    generates sentence objects.
    each is a dictionary with info on tokens, words, lemmas.  (trying to be like the corenlp json objects. well kind of.)
    AND a special 'parse_samples' attribute which is a LIST of full parse structures, each formatted as a list of (rel,govind,childind) triples.

    we're using ONE-BASED indexing as is the case in the standard conll-ish
    dependency format.  But note in this code we PREPEND a special 'ROOT' node.
    So the indexing is "one-based" relative to the original surface tokens, but
    it's pythonically zero-based relative to the ROOT-prepended sentence.

    note this code would have to be modified to take in a real conll format
    (with only 1 parse) as input, since it's *very* slightly different
    (it has a tab between the govindex and deprel.. the 'sample conll' format
    brendan made up doesn't)
    """
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
        sent['lemmas'] = [x['lemma'] for x in sent['tokens']]
        # assert False, "todo"
        parse_samples = []

        traditional_conll_format = len(rows[0][6].split())==1
        if traditional_conll_format:
            triples = [(row[7],row[6],row[0]) for row in rows]
            triples = [(r, int(g), int(c)) for (r,g,c) in triples]
            parse_samples.append(triples)  ## only one 'sample'
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
                parse_samples.append( triples )
        sent['parse_samples'] = parse_samples
        yield sent

def test_input(f):
    for sent in yield_conll_sentences(open(f)):
        print
        print sent['words']
        print sent['parse_samples']
        for samplenum,parse in enumerate(sent['parse_samples']):
            print (u"sample%d:" % samplenum),
            print u",  ".join(u"%s(%s, %s)" % (r, sent['words'][g], sent['words'][c]) for (r,g,c) in parse).encode("utf8")

if __name__=='__main__':
    eval(sys.argv[1])(*sys.argv[2:])
