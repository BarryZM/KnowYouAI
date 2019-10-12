from core.bots._base import Bot
from core.state import State
from _global.const import _Score
import random


class TaoLu(Bot):
    Wait = 1

    def __init__(self, dictionary, ai_being):
        super(TaoLu, self).__init__()
        self.ai_being = ai_being
        self.dictionary = dictionary
        self.user_id_last_query = {}
        self.tao_lu = {
            "你最近是不是又胖了": "那你为什么在我心里的分量越来越重了呢",
            "你属什么？": "不，你属于我",
            "这是我的手背, 这是我的脚背，那你是什么?": "你是我宝贝 ",
            "我想买一块地。": "你的死心塌地。",
            "莫文蔚的阴天，孙燕姿的雨天，周杰伦的晴天, 还有什么天 ": "都不如你找我聊天",
            "牛肉猪肉和羊肉，你猜我喜欢吃哪种肉 ": "不对，应该是你这块心头肉。",
            "你是什么血型？": "我的理想型",
            "生活就想海洋, 不要抱怨": "抱我 ",
            "你是要我多喝水吗": "我不喝水，我呵护你",
            "我一个人吃饭的时候会感到孤单": "但一个人吃鸡腿时就不会"
        }

    def activate_match(self, query, st):
        # 一定概率表达自己的心情
        relationship = self.ai_being.get_value("relationship", st.user_id) / 100
        return random.uniform(0, 1) < relationship * 0.2

    def activate_say(self, query, st):
        # user_id = st.user_id
        key_list = list(self.tao_lu.keys())
        q = random.choice(key_list)
        a = self.tao_lu[q]
        return "{}\n{}".format(q, a)

    def match(self, query, st: State):
        user_id = st.user_id
        if user_id not in self.user_id_table:
            self.user_id_table[user_id] = TaoLu.Init
            self.user_id_last_query[user_id] = ""
        if random.uniform(0, 1) < 0.1:
            if self.dictionary.is_praise_sentence(query) or self.user_id_table[user_id] != TaoLu.Init:
                return True, 1
        return False, 0

    def get_response(self, query, st: State):
        user_id = st.user_id
        key_list = list(self.tao_lu.keys())
        if self.user_id_table[user_id] == TaoLu.Init:
            ans = random.choice(key_list)
            self.user_id_table[user_id] = TaoLu.Wait
            self.user_id_last_query[user_id] = ans
        else:
            ans = self.tao_lu[self.user_id_last_query[user_id]]
            self.user_id_table[user_id] = TaoLu.Init
        return ans
