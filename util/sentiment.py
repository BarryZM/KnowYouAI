from _global.const import _Sentiment
import json
import random


class Sentiment:
    """
    计算各情感
    """

    # TODO 使用NN或多模态进行情绪识别
    def __init__(self, dictionary, user_profile, ai_being):
        self.dictionary = dictionary
        self.user_profile = user_profile
        self.ai_being = ai_being

    def get_user_sentiment(self, query, user_id):
        score = 0
        if self.dictionary.is_curse_sentence(query):
            score -= 1
        if self.dictionary.is_praise_sentence(query):
            score += 1
        # path = "./UserData/{}/user_profile.json".format(user_id)
        # user_profile = json.load(open(path, "r", encoding="utf-8"))
        # user_profile = self.user_profile.get("attitude",user_id)
        attiitude = self.user_profile.get("attitude", user_id)
        for word in attiitude:
            if word in query:
                if attiitude[word] == "like":
                    score += 1
                if attiitude[word] == "unlike":
                    score -= 1
        # TODO 使用NN进行文字情绪识别
        sentiment = _Sentiment.Normal
        if score > 0:
            sentiment = _Sentiment.Positive
        if score < 0:
            sentiment = _Sentiment.Negative
        return sentiment

    def get_ai_sentiment(self, query, user_id, user_sentiment):
        """
        获取AI的喜好情感
        :return:
        """
        # path = "./UserData/{}/ai_being.json".format(user_id)
        # ai_being = json.load(open(path, "r", encoding="utf-8"))
        # 获取喜好字段 含like的key
        score = 0

        for key in self.ai_being.get_key(user_id):
            if "like" in key:
                like_item = self.ai_being.get_value(key, user_id)
                for item in like_item:
                    # 用户提及过了喜欢的字段，就开森
                    if item in query:
                        score += 1
        sentiment = _Sentiment.Normal
        if score > 0 or random.uniform(0, 1) < (self.ai_being.get_value("relationship", user_id) / 100) and \
                        user_sentiment != _Sentiment.Negative:
            # relationship 越高，越容易开心
            sentiment = _Sentiment.Positive
        return sentiment

    def fit_sentiment(self, response, sentiment):
        """
        给response改写，体现出情感
        V1 加情感词
        :param response:
        :return:
        """
        # TODO Seq2seq改写
        table = [
            "哈哈，",
            "嘻嘻，",
            "嘿咻，",
            "哟西，",
        ]
        if sentiment == _Sentiment.Positive:
            word = random.choice(table)
            response = word + response
        return response
