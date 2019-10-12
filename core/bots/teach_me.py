from ._base import Bot
from core.state import State
from _global.const import _Score
import config
import random


class TeachMe(Bot):
    """
    请求学习，返回一个页面提醒用户教她学习
    为了不让用户乱访问，除了user_id外，会随机生成一串5-10的字符串作为key，写入user_profile文件
    让server端接受请求时校验
    """

    def __init__(self, user_profile, ai_being):
        super(TeachMe, self).__init__()
        self.user_profile = user_profile
        self.ai_being = ai_being

    def _create_key(self):
        alpaha = "abcdefghijklmnopqrstuvwxyz"
        Alpaha = alpaha.upper()
        number = "1234567890"
        k = random.randint(5, 11)
        key = random.choices(alpaha + Alpaha + number, k=k)
        return "".join(key)

    def activate_match(self, query, st: State):
        user_id = st.user_id
        no_attitude = self.user_profile.entity_no_attitude(user_id)
        if len(no_attitude) > 20 and random.uniform(0, 1) < 0.2:
            return True
        return False

    def activate_say(self, query, st):
        user_id = st.user_id
        no_attitude = self.user_profile.entity_no_attitude(user_id)
        key = self._create_key()
        # 写入user profile
        # 虽然保存在那，却是临时有效
        self.user_profile.write_pair(user_id, "key", key)
        url = "{host}/teach?user_id={user_id}&key={key}".format(host=config.HOST, user_id=user_id, key=key)
        ans = "{},我有{}不知道你怎么想的词汇哟。你有时间的话，可以点进来教一下我。\n{}" \
            .format(self.ai_being.get_value("your_name", st.user_id), len(no_attitude), url)
        return ans

    def match(self, query, st):
        """

        :param query:
        :param st:
        :return:
        """
        flag = (query == "我要教你")
        s = _Score.LevelNormal if flag else 0.
        return flag, s

    def get_response(self, query, st: State):
        user_id = st.user_id
        key = self._create_key()
        # 写入user profile
        # 虽然保存在那，却是临时有效
        self.user_profile.write_pair(user_id, "key", key)
        return "{host}/teach?user_id={user_id}&key={key}".format(host=config.HOST, user_id=user_id, key=key)
