#!/bin/bash
set -eux

# on hobbes, use:
# hobbes:~/parsemar % ln -s /home/sw/corenlp/stanford-corenlp-full-2017-06-09 corenlp

# WEIRD QUIRK: need to run this with working dir the same as the text files,
# because the first corenlp.sh step will output to the current directory.
# (or, there may be a way to give it output dir flags to change this)

here=$(dirname $0)/..
file=$1
predfile=${file}.pred

# tok/pos to .conllu.  need depparse annotator else conllu data is empty.
$here/corenlp/corenlp.sh -threads 5 -ssplit.eolonly true -tokenize.whitespace true -annotators tokenize,ssplit,pos,lemma,depparse -outputFormat conllu -file $file

# # run sampling parser
# java -XX:ParallelGCThreads=2 -cp "$here/target/classes/" edu.stanford.nlp.parser.nndep.DependencyParser \
#   -model $here/stuff/english_UD.gz \
#   -testFile ${file}.conllu \
#   -outFile $predfile \
#   -numSamples $nsample
