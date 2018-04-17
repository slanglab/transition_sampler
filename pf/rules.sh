#!/bin/zsh
set -eux
# rule-based testset-only pipeline

echo "============ top/greedy parse ==========="
# python pfrules.py gorules =(cat batches/batch_test_sent_??.conllu) 1 PoliceKillingsExtraction-ments-v1/test.json > allsent_greedy.out
grep '^OUT' allsent_greedy.out | cut -f2 | python  ~/policefatalities_emnlp2017/code/eval/evaluation.py

# echo "============== 1 sample ==============="
# python pfrules.py gorules =(cat batches_10samp/batch_test_sent_??.pred) 1 PoliceKillingsExtraction-ments-v1/test.json > allsent_1samp.out
# grep '^OUT' allsent_1samp.out | cut -f2 | python  ~/policefatalities_emnlp2017/code/eval/evaluation.py

# echo "============== 10 samples ==============="
# python pfrules.py gorules =(cat batches_10samp/batch_test_sent_??.pred) 10 PoliceKillingsExtraction-ments-v1/test.json > allsent_10samp.out
# grep '^OUT' allsent_10samp.out | cut -f2 | python  ~/policefatalities_emnlp2017/code/eval/evaluation.py
#

echo "=============== 100 samples standard"
# python pfrules.py gorules =(cat batches_100samp/*test_sent*.pred) 100 PoliceKillingsExtraction-ments-v1/test.json > allsent_100samp.out
grep '^OUT' allsent_100samp.out | cut -f2 | python  ~/policefatalities_emnlp2017/code/eval/evaluation.py

echo "================== sampleMAP with 100 samples"
# python pfrules.py gorules test_samplemap_100samp  1 PoliceKillingsExtraction-ments-v1/test.json > allsent_samplemap_100samp.out                               
grep '^OUT' allsent_samplemap_100samp.out | cut -f2 | python  ~/policefatalities_emnlp2017/code/eval/evaluation.py


