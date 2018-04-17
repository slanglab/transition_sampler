#!/bin/zsh
set -eux

# preproc pipeline
# prefix=test
prefix=train

sentment_file=PoliceKillingsExtraction-ments-v1/$prefix.json
python prepare_sents.py < $sentment_file > ${prefix}_sent.txt
wc -l ${prefix}_sent.txt
# stupid corenlp prefers to work on files in same dir
split -l 10000 ${prefix}_sent.txt batch_${prefix}_sent_
print -l batch_${prefix}_sent_?? | parallel -j10 ./parsetext.sh


