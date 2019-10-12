import json
import config


class AIBeing:
    def __init__(self, dictionary):
        self.userid_ai_being = {}
        self.userid_update = {}  # 每个user id更新的次数，更新一定次数后，定期序列化
        self.dictionary = dictionary

    def get_key(self, user_id):
        self.load(user_id)
        ai_being = self.userid_ai_being[user_id]
        return ai_being.keys()

    def get_value(self, key, user_id, default=None):
        self.load(user_id)
        ai_being = self.userid_ai_being[user_id]
        return ai_being.get(key, default)

    def load(self, user_id):
        if user_id not in self.userid_ai_being:
            path = "./UserData/{}/ai_being.json".format(user_id)
            ai_being = json.load(open(path, "r", encoding="utf-8"))
            self.userid_ai_being[user_id] = ai_being
            self.userid_update[user_id] = 0

    def updata(self, query, user_id):
        self.load(user_id)
        # 更新对用户的好感度
        ai_being = self.userid_ai_being[user_id]
        score = ai_being["relationship"]
        for key in ai_being:
            if "like" in key:
                like_item = ai_being[key]
                for item in like_item:
                    # 用户提及过了喜欢的字段，就开森
                    if item in query:
                        score += score / 100
        # 检测用户表达
        if self.dictionary.is_praise_sentence(query):
            score += score / 100
        elif self.dictionary.is_curse_sentence(query):
            score -= score / 100
        if score > 100:
            score = 100.
        if score < 0:
            score = 0.
        ai_being["relationship"] = score
        self.userid_update[user_id] += 1
        if (self.userid_update[user_id] + 1) % config.AI_BEING_UPDATE_ITER == 0:
            path = "./UserData/{}/ai_being.json".format(user_id)
            json.dump(ai_being, open(path, "w", encoding="utf-8"))
