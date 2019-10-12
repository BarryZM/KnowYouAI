import glob
import math
import json
import jieba
from jieba import posseg

token = jieba.Tokenizer()
file = glob.glob("./../jieba_dict/*.txt")
for fp in file:
    token.load_userdict(fp)
pos_token = posseg.POSTokenizer(token)
file = glob.glob("./*.txt")
item_ids = 0
sentence_ids = 0  # 句子条目
word_bag = set()
PMI_DICT = {}  # key(wj,wi),value  log(P(wi|wj)/p(wi))
WI = {}
for fp in file:
    for line in open(fp, "r", encoding="utf-8"):
        line_list = line.strip().split("####")
        if len(line_list) != 3:
            continue
        query, response, sentiment = line_list
        sentence_ids += 1
        query_token = [word for word, tag in pos_token.lcut(query) if "n" in tag]
        for to in query_token:
            word_bag.add(to)
        response_token = [word for word, tag in pos_token.lcut(response) if "n" in tag]
        for to in response_token:
            WI[to] = WI.get(to, 0) + 1
            word_bag.add(to)
        # query中抽取wJ，response中抽取wi
        for qt in query_token:
            for rt in response_token:
                key = (qt, rt)
                PMI_DICT[key] = PMI_DICT.get(key, 0) + 1

    print("Load :", fp)

print("build PMI")
for key in PMI_DICT:
    wj, wi = key
    pwj_wi = PMI_DICT[key] / sentence_ids
    pwi = WI[wi] / sentence_ids
    PMI_DICT[key] = math.log(pwj_wi / pwi)

print("Size of word bag:", len(word_bag))
print("PMI size:", len(PMI_DICT))
json.dump({
    "word_bag": word_bag,
    "PMI": PMI_DICT
}, open("./pmi.json", "w", encoding="utf-8"))
