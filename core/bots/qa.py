from ._base import Bot
from core.state import State
from _global.const import _Score
from urllib.parse import quote
import random
import config
import re
import json

_search_standard = [
    {
        "pattern": "电影",
        "mode": "in",
        "standard": "最近有什么电影上映呢"
    },
    {
        "pattern": "那{0,1}(|今|后|明){0,1}天{0,1}(?P<city>[^的|^最近|.]{0,4})(最近){0,1}的{0,1}天气怎么样",
        "mode": "re",
        "group": ["city"],
        "standard": "{city}天气"
    },
    {
        "pattern": "查询天气",
        "mode": "re",
        "standard": "天气"
    },
    {
        "pattern": "(现在){0,1}(?P<city>[^的|^现在|.]{0,4})(现在){0,1}几点",
        "mode": "re",
        "group": ["city"],
        "standard": "{city}时间现在几点"
    },
    {
        "pattern": "(现在){0,1}(?P<city>[^的|^现在|.]{0,4})的{0,1}时间",
        "mode": "re",
        "group": ["city"],
        "standard": "{city}时间现在几点"
    }

]


class _KG:
    def __init__(self, infer_tool):
        self.infer_tool = infer_tool

    def search(self, entity, attr, cy):
        result_entity = self.infer_tool.get_detail_Realation(entity, attr, cy)
        if len(result_entity) == 0:
            ans = random.choice(
                ["不知道", "不懂", "没有找到", "不懂略略略"]
            )
        else:
            ans = "{}".format(",".join([en["value"] for en in result_entity]))
        return ans


class QA(Bot):
    def __init__(self, infer_tool):
        super(QA, self).__init__()
        self.kg = _KG(infer_tool)
        self.math_re = re.compile("(\d{1,}(\+|\-|\*|/|除以)\d{1,})(等于|=){0,1}")
        # 匹配成功的正则表达式
        self.engine_qa = [
            self.math_re,
            re.compile("(?P<question>.{0,})是什么(日子|诗)"),
            re.compile(r"(多少号|几多号|什么日子|几号|时间|几点)\?{0,1}$"),
            re.compile(r"什么电影看"),
            re.compile(r"什么电影上映"),
            re.compile(r"^(最近){0,1}上映的电影$"),
            re.compile(r"^查询天气$"),
            re.compile(r"(今|后|明){0,1}天{0,1}(?P<city>[^的|.]{0,4})的{0,1}天气.{0,}(怎么样|情况)"),
            re.compile(r"[^你]是什么\?{0,1}$"),
            re.compile(r"[^你]是谁\?{0,1}$"),
            re.compile(r"[^你]是谁拍的\?{0,1}$"),
            re.compile(r"[^你]是谁写的\?{0,1}$"),
            re.compile(r"[^你]怎么养\?{0,1}$"),
            re.compile(r"[^你]怎么煮\?{0,1}$"),
            re.compile(r"[^你](多大|多少岁|喜欢吃什么|喜欢玩什么)\?{0,1}$"),
            re.compile(r".{5,}下一句\?{0,1}$")
        ]

        self.kg_qa = [
            {
                "pattern": re.compile(r"请问(你知道){0,1}(?P<entity>.{0,})的(?P<attr>.{0,})是谁吗{0,1}"),
                "query": "match (p)-[r:{relationship}]->(p1) where p.value=\'{entity}\' return p1"
            },
            {
                "pattern": re.compile(r"(?P<entity>.{0,})的(?P<attr>.{0,})都有谁\?{0,1}"),
                "query": "match (p)-[r:{relationship}]->(p1) where p.value=\'{entity}\' return p1"
            },
            # {}
        ]

    def helper(self):
        info = [
            "你可以输入1+1数学表达式来计算噢",
            "你可以输入 最近有什么电影上映 来查看最新的电影信息",
            "你可以输入形如 落下与孤鹜齐飞的下一句 来查看古诗古文相关的知识",
            "你可以输入形如 玉露怎么养 来查看综合知识"
        ]
        return info

    def _standardlize(self, text):
        """
        暴力规则,将问题标准化
        :param text:
        :return:
        """
        new_text = text
        for rule in _search_standard:
            pattern = rule["pattern"]
            mode = rule.get("mode", "equal")
            # print(text, pattern, mode)
            if mode == "equal" and text == pattern:
                new_text = rule["standard"]
            elif mode == "in" and pattern in text:
                new_text = rule["standard"]
            elif mode == "re":
                r = re.search(pattern, text)
                if r is not None:
                    groups = rule.get("group", [])
                    params = {}
                    for g in groups:
                        value = r.group(g)
                        params[g] = value
                    new_text = rule["standard"].format(**params)
        return new_text

    def match(self, query, st: State):
        user_id = st.user_id
        if user_id not in self.user_id_table:
            self.user_id_table[user_id] = QA.Init
        flg = any([pattern.search(query) for pattern in self.engine_qa] + \
                  [item["pattern"].search(query) for item in self.kg_qa] + [self.user_id_table[user_id]])
        s = _Score.LevelNormal if flg else 0.
        return flg, s

    def activate_match(self, query, st):
        return "无聊" in query and random.uniform(0, 1) < 0.1

    def get_response(self, query, st: State):
        # 先检查KG内是否有
        re_result = None
        cy = None
        for kgqa in self.kg_qa:
            pattern = kgqa["pattern"]
            cy = kgqa["query"]
            re_result = pattern.search(query)
            if re_result is not None:
                break
        if re_result is not None:
            entity = re_result.group("entity")
            attr = re_result.group("attr")
            ans = self.kg.search(entity, attr, cy)
            return ans
        else:
            match_result = self.math_re.search(query)
            if match_result is not None:
                exp = match_result[0]
                exp = exp.replace("除以", "/").replace("等于", "").replace("=", "")
                resutl = eval(exp)
                return str(resutl)
            new_query = self._standardlize(query)
            # 返回一个链接
            #  "#"表示特殊回复，后面的字段用’_‘来表示各属性,根据各环境自行解析
            baidu_url = 'https://www.baidu.com/s?wd={}'.format(quote(new_query))
            bing_url = "https://cn.bing.com/search?q={}".format(quote(new_query))
            google_url = "https://www.google.com/search?q={}".format(quote(new_query))
            ans = {
                "baidu_url": "{}".format(baidu_url),
                "bing_url": "{}".format(bing_url),
                "google_url": "{}".format(google_url)
            }
            return "#json:{}".format(json.dumps(ans))
