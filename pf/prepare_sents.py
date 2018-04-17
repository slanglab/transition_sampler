import sys,json,re
for line in sys.stdin:
# for line in open("PoliceKillingsExtraction-ments-v1/test.json"):
    sentment = json.loads(line)
    print re.sub(r'\s+'," ", sentment['sent_alter']).encode("utf8")
