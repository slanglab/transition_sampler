from __future__ import division
from collections import Counter
import math,sys,termcolor
goldfile,predfile = sys.argv[1:]

ll = 0
brier=0
ncorrect=0
ntotal = 0

for gline,pline in zip(open(goldfile),open(predfile)):
    if not gline.strip():
        print
        continue
    goldparts = gline.strip().split("\t")
    child,goldgov,goldrel = goldparts[0],goldparts[6],goldparts[7]
    predparts = pline.strip().split("\t")
    assert predparts[0:2]==goldparts[0:2]
    samples = [x.split() for x in predparts[6:]]
    samples = [(gov,rel) for gov,rel in samples]
    counts = Counter(samples)
    n=len(samples)
    preds = [(c/n, gov,rel) for (gov,rel),c in counts.most_common()]
    predent = sum(-p*math.log(p) for p,gov,rel in preds)
    predprob = counts[goldgov,goldrel] / n
    toppred = counts.most_common()[0][0]

    # for p,gov,rel in preds:
    #     isgold = int( (gov,rel) == (goldgov,goldrel) )
    #     print "%s-%s %s %s" % (gov,rel, p,isgold)
    # continue

    predstr = " ".join(
                termcolor.colored("%s-%s" % (gov,rel), 
                'red' if (gov,rel)==(goldgov,goldrel) else 'grey',
                attrs=['bold'] if (gov,rel)==(goldgov,goldrel) else []) + (":%.2f" % p)
                for (p,gov,rel) in preds)
    out = [child,goldparts[1].ljust(15),goldparts[3].ljust(7),
            ("gold %s-%s" % (goldgov,goldrel)).ljust(20),
            "predprob %.3f" % predprob,
            ("corr %s" % int((toppred)==(goldgov,goldrel))),
            "ent %.3f" % predent,
            predstr,
        ]
    brier += (1-predprob)**2
    ntotal += 1
    ncorrect += (toppred)==(goldgov,goldrel)
    print "\t".join(out)
# sys.exit()
print "MBR ACC", ncorrect/ntotal
print "BRIER", (brier/ntotal)
