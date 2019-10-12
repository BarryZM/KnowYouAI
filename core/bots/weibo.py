from ._base import Bot
from core.state import State
from _global.const import _Score
from _global.regex import weibo_re
import random
import config
import util


class WeiBo(Bot):
    WaitUserName = 1

    def __init__(self, text_tool):
        super(WeiBo, self).__init__()
        self.text_tool = text_tool
        self._user_id_error = {}  # 输入非法信息，超出一次,第二次检测错误时退出

    def helper(self):
        return ["你可以说 我想看[name]的微博 就可以查看[name]最新的微博噢"]

    def match(self, query, st: State):
        # if self.state != Bot.Init:
        #     return True, 1
        reg = weibo_re.search(query)
        user_id = st.user_id
        if user_id not in self.user_id_table:
            self.user_id_table[user_id] = WeiBo.Init
            self._user_id_error[user_id] = 0
        flg = (reg is not None) or self.user_id_table[user_id] != WeiBo.Init
        s = _Score.LevelNormal if flg else 0.
        return flg, s

    def activate_match(self, query, st: State):
        return "无聊" in query and random.uniform(0, 1) < 0.9

    def get_response(self, query, st: State):
        user_id = st.user_id
        user = None
        # state = self.user_id_table[user_id]
        if self.user_id_table[user_id] == WeiBo.Init:
            reg = weibo_re.search(query)
            name = reg.group("name")
            if name != "":
                user = name
            else:
                words = self.text_tool.pos_lcut(query)

                # print(list(words)) # 迭代器用了list后，就不能迭代了要复位。
                for word, tag in words:
                    if tag == "nr":
                        user = word
                        break
        else:
            # 非INIT状态，找人名
            reg = weibo_re.search(query)
            if reg is not None:
                name = reg.group("name")
                if name != "":
                    user = name
            else:
                words = self.text_tool.pos_lcut(query)
                for word, tag in words:
                    if tag == "nr":
                        user = word
                        break
        # 填充user后访问
        if user is None or len(user) == 0:
            # 如果是第一次就问问，如果是第二次没找到就算了
            if self.user_id_table[user_id] == WeiBo.Init:
                ans = "你要看谁的微博呢？"
                self.user_id_table[user_id] = WeiBo.WaitUserName
            elif self._user_id_error[user_id] < 1:
                self._user_id_error[user_id] += 1
                ans = "没有检测到人名哦,想想再答？"
                self.user_id_table[user_id] = WeiBo.WaitUserName
            else:
                ans = "退出微博检索了，我们聊点别的吧"
                self.user_id_table[user_id] = WeiBo.Init
                self._user_id_error[user_id] = 0
        else:
            try:
                info = util.http_client.WeiBo.getInfo(user)
                # 只关注最新的时间
                if len(info) > 0:
                    ans = "bug啦"
                    for item in info:
                        weibo_update = item["time"]
                        context = item["content"]
                        if len(context) > 0:
                            ans = "{}在{}更新了微博:\n{}".format(user, weibo_update, context)
                            break
                else:
                    ans = "{}的微博没有信息诶".format(user)
                self.user_id_table[user_id] = WeiBo.Init
            except Exception as e:
                ans = "似乎网络有些问题哦。"
        return ans
