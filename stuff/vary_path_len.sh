for t in 2 3 4 5 6 7 8; do 
    echo "===" $t
    echo METHOD greedy
    python higher.py --tlen $t --treepred --greedy en-ud-dev.conllu preds1/full.pred.argmax
    echo METHOD sample1000
    python higher.py --tlen $t --treepred en-ud-dev.conllu preds1/full.pred.nsample=1000.temp=1
    echo METHOD sample100
    python higher.py --tlen $t --treepred en-ud-dev.conllu preds1/full.pred.nsample=100.temp=1

done
