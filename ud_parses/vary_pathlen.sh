#!/bin/zsh

for tlen in 1 2 3 4 5 6 7 8 9 10; do
  echo "=== $tlen"

# python ../stuff/higher.py --edgepred --tlen $tlen --verbose en-ud-dev.conllu en-ud-dev.pred > edgepred.tlen=$tlen.100sample
#   
# python ../stuff/higher.py --greedy --edgepred --tlen $tlen --verbose en-ud-dev.conllu en-ud-dev-greedy.pred > edgepred.tlen=$tlen.greedy

python ../stuff/higher.py --greedy --edgepred --tlen $tlen --verbose en-ud-dev.conllu en-ud-dev.mcmap > edgepred.tlen=$tlen.mcmap
done

