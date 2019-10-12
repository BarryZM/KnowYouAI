import config
import os


class Dictionary:
    """
    全局字典
    记录一些词，不用反复访问
    """

    def __init__(self):
        self.praise_sentence = [line.strip() for line in open(config.PRAISE_PATH, "r", encoding="utf-8")]
        self.curse_sentence = [line.strip() for line in open(config.CURSE_PATH, "r", encoding="utf-8")]
        # 字符表情包
        self.QAQ = [line.strip() for line in open(config.QAQ_PATH, "r", encoding="utf-8")]
        # 不允许出现在回复的词
        self.ban_word = [line.strip() for line in open(config.BAN_PATH, "r", encoding="utf-8")]
        # 停止符
        self.stop_word = [line.strip() for line in open(config.STOP_WORD, "r", encoding="utf-8")]
        # 结束字符
        self.end_word = [line.strip() for line in open(config.END_WORD, "r", encoding="utf-8")]
        # 确认字符
        self.affirm_word = [line.strip() for line in
                            open(os.path.join(config.AFFIME_PATH, "affirm.txt"), "r", encoding="utf-8")]

    def is_end(self, query):
        for end_word in self.end_word:
            if end_word in query:
                return True
        return False

    def is_praise_sentence(self, sentence):
        for sen in self.praise_sentence:
            if sen in sentence:
                return True
        return False

    def is_curse_sentence(self, sentence):
        for sen in self.curse_sentence:
            if sen in sentence:
                return True
        return False
