"""
Give this CoreNLP JSON on stdin: one document per line.
This iterates through the sentences and shows the dependencies
unlike conll output, this shows 'enhanced' versions where there can be
multiple parents for a word; e.g. control

Output examples: see README_viewdeps.md

Another example:
'
~/corenlp_jsontsv % ./run.sh -annotators tokenize,ssplit,pos,depparse
[..loading..]
[main] INFO corenlp_jsontsv.Run - Waiting for documents on standard input.
"They want us to be respectful."
[..output, copy to clipboard..]

~/corenlp_jsontsv % pbpaste|python viewdeps.py

ROOT_0 They_1 want_2 us_3 to_4 be_5 respectful_6 ._7
 1 They       PRP  <-nsubj------- want_2
 2 want       VBP  <-ROOT-------- ROOT_0
 3 us         PRP  <-dobj-------- want_2
 3 us         PRP  <-nsubj:xsubj- respectful_6
 4 to         TO   <-mark-------- respectful_6
 5 be         VB   <-cop--------- respectful_6
 6 respectful JJ   <-xcomp------- want_2
 7 .          .    <-punct------- want_2
"""

import sys,json,re

def convert_from_corenlp_sent(json_obj):
    # input is from corenlp json format for one sentence
    # returns a reduced format for our purposes
    deps = json_obj['enhancedPlusPlusDependencies']
    tokens = json_obj['tokens']
    tokens = [{'pos':'ROOT', 'word':'ROOT'}] + tokens
    deps = [ (x['dep'],x['governor'],x['dependent']) for x in deps]
    return {'tokens':tokens, 'deps':deps}

def normalize(w):
    return re.sub(r'(.)\1{3,}', r'\1\1\1\1', w)

# print normalize("hi")
# print normalize("hiiiiiiiii")
# sys.exit()

def viewdeps_depfirst(sent):
    if 'deps' not in sent: sent = convert_from_corenlp_sent(sent)
    toks = [tok['word'] for tok in sent['tokens']]
    toks = [normalize(w) for w in toks]
    print u" ".join(u"%s_%s" % (w,i) for (i,w) in enumerate(toks)).encode("utf-8")
    sent['deps'].sort(key=lambda (r,g,c): (c,g,r))
    rlen = max(len(r) for (r,g,c) in sent['deps'])
    wlen = max(len(w) for w in toks)
    plen = max(len(t['pos']) for t in sent['tokens'])
    for (r,g,c) in sent['deps']:
        rel = "<-%s-" % r.ljust(rlen,"-")
        # print "%2d %s %s %2d %s" % (c, toks[c].ljust(wlen), rel, g, toks[g],)
        print u"{cind:2d} {word} {pos} {rel} {govword}_{govind}".format(
                cind=c, word=toks[c].ljust(wlen),
                pos=sent['tokens'][c]['pos'].ljust(plen),
                rel=rel, govword=toks[g], govind=g
            ).encode("utf-8")

def viewdeps_govfirst(sent):
    if 'deps' not in sent: sent = convert_from_corenlp_sent(sent)
    toks = [tok['word'] for tok in sent['tokens']]
    toks = [normalize(w) for w in toks]
    # toks = ["%s/%s" % (w,sent['tokens'][i]['pos']) for (i,w) in enumerate(toks)]

    colmap = smart_color_analyis(sent)
    # wordind = (u"%s_%s" % (w,i) for (i,w) in enumerate(toks))
    wordind = toks
    wordind = [u"%s%s%s" % (colmap[i], wi, colors.reset) if i in colmap else wi
            for (i,wi) in enumerate(wordind)]
    print u" ".join(wordind).encode("utf-8")
    sent['deps'].sort(key=lambda (r,g,c): (g,c,r))
    rlen = max(len(r) for (r,g,c) in sent['deps'])
    prevg=None
    wlen = max(len(w) for w in toks)
    for (r,g,c) in sent['deps']:
        rel = "-%s->" % r.ljust(rlen,"-")
        start = u"%2d %s" % (g, toks[g].ljust(wlen))
        if g==prevg:
            start = ' '*len(start)
        else:
            if g in colmap:
                start = u"%2d %s%s%s" % (g, colmap[g], toks[g].ljust(wlen), colors.reset)

        prevg=g
        cout = "%s_%s" % (toks[c], c)
        if c in colmap:
            cout = "%s%s%s" % (colmap[c], cout, colors.reset)
        print (u"%s %s %s" % (start, rel, cout)).encode("utf-8")

class colors:
    reset='\033[0m'
    bold='\033[01m'
    disable='\033[02m'
    underline='\033[04m'
    reverse='\033[07m'
    strikethrough='\033[09m'
    invisible='\033[08m'
    class fg:
        black='\033[30m'
        blue='\033[34m'
        cyan='\033[36m'
        darkgrey='\033[90m'
        green='\033[32m'
        lightblue='\033[94m'
        lightcyan='\033[96m'
        lightgreen='\033[92m'
        lightgrey='\033[37m'
        lightred='\033[91m'
        orange='\033[33m'
        pink='\033[95m'
        purple='\033[35m'
        red='\033[31m'
        yellow='\033[93m'
    class bg:
        black='\033[40m'
        blue='\033[44m'
        cyan='\033[46m'
        green='\033[42m'
        lightgrey='\033[47m'
        orange='\033[43m'
        purple='\033[45m'
        red='\033[41m'

# for c in sorted(colors.fg.__dict__):
#     cc = getattr(colors.fg,c)
#     print "%s hihi %s hihi %s" % (cc, c, colors.reset)
# sys.exit()

colchoices = ['darkgrey','blue','red','cyan','green','orange','purple','lightblue','lightred','pink']
assert len(colchoices)==len(set(colchoices))
colchoices = [getattr(colors.fg,c) for c in colchoices]

def smart_color_analyis(sent):
    colormap = {}
    all_govs = sorted({g for (r,g,c) in sent['deps']})
    for govnum,govind in enumerate(all_govs):
        colormap[govind] = colchoices[ govnum % len(colchoices) ]
    return colormap

if __name__=='__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('-g','--gov-first', help="Gov-centric ordering of tuples. Default is child-centric, which yields surface order.",  action='store_true')
    args = p.parse_args()

    viewfn = viewdeps_govfirst if args.gov_first else viewdeps_depfirst

    for line in sys.stdin:
        doc = json.loads(line.split("\t")[-1])
        for sent in doc['sentences']:
            print
            sys.stdout.write("= S%s =\t" % sent.get("index"))
            viewfn(sent)
