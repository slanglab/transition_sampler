"""take "sample conll" on stdin"""
from __future__ import division
from collections import Counter
import math,sys #,termcolor

for pline in sys.stdin:
    if not pline.strip():
        print
        continue
    predparts = pline.strip().split("\t")
    samples = [x.split() for x in predparts[6:]]
    samples = [(gov,rel) for gov,rel in samples]
    counts = Counter(samples)
    n=len(samples)
    preds = [(c/n, gov,rel) for (gov,rel),c in counts.most_common()]
    # predent = sum(-p*math.log(p) for p,gov,rel in preds)
    toppred = counts.most_common()[0][0]

    predstr = " ".join(
                    "%s-%s:%.2f" % (gov,rel,p)
                for (p,gov,rel) in preds)
    out = [predparts[0].ljust(4), predparts[1].ljust(15), predparts[3].ljust(7),
            predstr,
        ]
    print " ".join(out)
