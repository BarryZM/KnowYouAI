import jieba
from jieba.posseg import POSTokenizer
import config
import os
import logging

jieba.setLogLevel(logging.INFO)


class TextTool:
    def __init__(self):
        self.token = jieba.Tokenizer()
        file = [x.path for x in os.scandir(config.JIEBA_DICT_PATH) if x.path.endswith("txt")]
        for fp in file:
            self.token.load_userdict(fp)
        self.pos_token = POSTokenizer(self.token)

    def lcut(self, query):
        return self.token.lcut(query)

    def pos_lcut(self, query):
        return self.pos_token.lcut(query)

