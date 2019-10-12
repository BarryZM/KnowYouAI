import random


class Ask:
    """
    v1 使用规则解决，考虑实体的类型，以及实体的共现
    """

    # TODO Learning2Ask

    def __init__(self):
        self._ask_list = [
            [("people_name",), ["{people_name}怎么了"]],
            [("weather",), ["躲在家里吧", "要不去浪吧", "出门爽爽"]],
            [("movie",), ["好看么", "听说还行"]],
            [("like", "movie"), ["听说有点棒棒", "棒棒哒"]],
            [("like", "weather"), ["{weather}好呀,舒服", "{weather}最适合了"]],
            [("like", "people_name"), ["为什么喜欢{people_name}", "{people_name}有哪里吸引你的么"]],
            [("unlike", "people_name"), ["为什么讨厌{people_name}", "{people_name}是坏人么", "{people_name}有多坏"]],
        ]
        self._defualt = ["怎么了", "什么事", "咋回事呀"]

    def _list_elem_equal(self, l1, l2):
        if len(l1) != len(l2):
            return False
        for elem1, elem2 in zip(l1, l2):
            if elem1 not in l2:
                return False
            if elem2 not in l1:
                return False
        return True

    def ask(self, query, entitys):
        type_value = {}

        for ent in entitys:
            for t in ent.type:
                type_value[t] = ent.entity
        # 从query的语法上解释出一些type
        other = []
        if "喜欢" in query and "不喜欢" not in query:
            other.append("like")
        if "不喜欢" in query:
            other.append("unlike")
        key = list(type_value.keys()) + other
        ask_list = self._defualt
        for ask_key, ask_list_candidate in self._ask_list:
            if self._list_elem_equal(key, ask_key):
                ask_list = ask_list_candidate
                break
        result = random.choice(ask_list)
        result = result.format(**type_value)
        return result
