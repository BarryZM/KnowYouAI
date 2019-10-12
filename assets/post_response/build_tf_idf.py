import glob
import math
import json
import jieba

token = jieba.Tokenizer()
file = glob.glob("./../jieba_dict/*.txt")
for fp in file:
    token.load_userdict(fp)
file = glob.glob("./*.txt")
item_ids = 0
TF = {}
IDF = {}
TF_IDF = {}
sentence_ids = 0  # 句子条目
for fp in file:
    for line in open(fp, "r", encoding="utf-8"):
        line_list = line.strip().split("####")
        if len(line_list) != 3:
            continue
        query, response, sentiment = line_list
        print("Deal:", query, response)
        query_keyword = token.lcut(query)
        for word in query_keyword:
            TF[word] = TF.get(word, 0) + 1
        for word in set(query_keyword):
            IDF[word] = IDF.get(word, 0) + 1
        sentence_ids += 1

        response_keyword = token.lcut(response)
        for word in response_keyword:
            TF[word] = TF.get(word, 0) + 1
        for word in set(response_keyword):
            IDF[word] = IDF.get(word, 0) + 1
        sentence_ids += 1

for word in TF:
    tf_ = TF[word]
    idf_ = math.log(sentence_ids / IDF[word])
    TF_IDF[word] = tf_ * idf_

json.dump(
    TF_IDF,
    open("./tf_idf.json", "w", encoding="utf-8")
)
print("OK")
