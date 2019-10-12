from ._base import Bot
from core.state import State
from _global import regex
from _global.const import _Score
import random
import requests


class New(Bot):
    def __init__(self):
        super(New, self).__init__()

    def match(self, query, st):
        reg = regex.new_re.search(query)
        flag = (reg is not None)
        s = _Score.LevelNormal if reg else 0.
        return flag, s

    def activate_match(self, query, st):
        return "无聊" in query and random.uniform(0, 1) < 0.1

    def helper(self):
        return ["你可以说 有什么(头条|社会|国内|娱乐|体育|军事|科技|财经|时尚)新闻 来查看新闻哦"]

    def _get_new(self, type_):
        params = {
            "type": type_,
            "key": "91ece343c8df34c3b801c4765af796cc",
        }
        URL = "http://v.juhe.cn/toutiao/index"
        response = requests.get(URL, params)
        json_data = response.json()
        result = json_data["result"]
        news_list = []
        if result["stat"] == '1':
            for elem in result["data"][:5]:
                news_list.append("来自{}的消息:{}。".format(elem["author_name"], elem["title"]))
        return "\n".join(news_list)

    def get_response(self, query, st: State):
        type_ = "top"
        text = query
        if "社会" == text:
            type_ = "shehui"
        elif "国内" in text:
            type_ = "guonei"
        elif "娱乐" in text:
            type_ = "yule"
        elif "体育" in text:
            type_ = "tiyu"
        elif "军事" in text:
            type_ = "junshi"
        elif "科技" in text:
            type_ = "keji"
        elif "财经" in text:
            type_ = "caijing"
        elif "时尚" in text:
            type_ = "shishang"
        ans = self._get_new(type_)
        return ans
