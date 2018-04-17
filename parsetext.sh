#!/bin/bash
set -eux
here=$(dirname $0)

# starting from text
file=$1
predfile=${file}.pred

# tok/pos to .conllu.  need depparse annotator else conllu data is empty.
# NOTE: this is using THEIR sentence splitter and tokenizer.  see tokenizer.whitespace in http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.703.3184&rep=rep1&type=pdf to override
$here/corenlp/corenlp.sh -annotators tokenize,ssplit,pos,lemma,depparse -outputFormat conllu -file $file

# run sampling parser
builddir=target_prebuilt   # checked-in for convenience
# builddir=target            # presumably do this if need to re-compile
java -cp "$here/$builddir/classes/" edu.stanford.nlp.parser.nndep.DependencyParser \
  -model $here/stuff/english_UD.gz \
  -testFile ${file}.conllu \
  -outFile $predfile \
  -numSamples 100 

# to view, something like:
# python stuff/higher.py -v --edgepred --tlen 1 pf1.txt.conllu pf1.txt.pred
