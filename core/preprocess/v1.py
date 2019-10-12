from core.preprocess._base import PreProcess
from core.state import State
import re
from _global import regex, global_entity_tool, EntityObj


class PreProcessV1(PreProcess):
    """
    第一个版本的预处理
    功能：
    使用规则处理指代
    """

    # TODO: 消歧义
    def __init__(self):
        super(PreProcessV1, self).__init__()

    # 处理问句
    def _question_fill(self, query):
        if regex.why.search(query):
            n = None
            v = None
            a = None
            user_input_seg = self.st.get_last_AI_record().segment
            for word, tag in user_input_seg:
                if "n" in tag:
                    n = word
                if "v" in tag:
                    v = word
                if "a" in tag:
                    a = word
            new_query = "为什么{n}{s}".format(n=n or "", s=v or a)
        elif regex.why2.search(query):
            ai_input = self.st.get_last_AI_record().content
            new_query = ai_input + query
        else:
            new_query = query
        return new_query

    def _clean_pronoun(self, query):
        """
        根据上下指代的问题，只能一轮
        :param query:
        :return:
        """

        if len(self.st._dialogue_window) < 2:
            """
            没上下文，不弄
            """
            return query
            # 上文聊到的实体
        # old_query = query
        new_query = query
        # print(self.st.dialogue_window)
        user_input_entity = self.st.get_last_User_record().entity
        AI_response_entity = self.st.get_last_AI_record().entity
        # 根据类型整合在一起，若同类型则优先放好最新的
        entity_dict = {}
        for item in AI_response_entity:
            if not isinstance(item, EntityObj):
                continue
            type_ = item.type
            value = item.entity
            if isinstance(type_, (list, tuple)):
                for t_ in type_:
                    entity_dict[t_] = value
        for item in user_input_entity:
            if not isinstance(item, EntityObj):
                continue
            type_ = item.type
            value = item.entity
            if isinstance(type_, (list, tuple)):
                for t_ in type_:
                    if t_ not in entity_dict:
                        entity_dict[t_] = value
        ###
        # 下面的是解决
        # 最近上海的天气
        # 那广州呢？
        # 的情况
        ###
        reg = regex.content_pattern1.search(query)

        if reg is not None:
            entity = global_entity_tool.extract(query)
            if len(entity) == 1:
                # 一般这种情况只有一个实体
                item = entity[0]
                type_ = item.type if isinstance(item.type, str) else item.type[0]
                if type_ in entity_dict:
                    # print(self.st.dialogue_window)
                    record = self.st.get_last_User_record()  # self.st.dialogue_window[-2]['content']
                    # print(record)
                    new_query = record.content
                    old_value = entity_dict[type_]
                    new_query = new_query.replace(old_value, item.entity)
        ###
        # 下面的是解决
        # 兔子喜欢菠萝(AI)
        # 他喜欢什么电影
        # 的情况
        ###
        # 在query中寻找代词,用上文的entity代入
        else:
            # pros = util.global_pronoun_tool.extract(query)
            pros = [{"pronoun": item.pros, "type": item.type} for item in AI_response_entity] + \
                   [{"pronoun": item.pros, "type": item.type} for item in user_input_entity]
            for item in pros:
                type_ = item["type"]
                if isinstance(type_, str):
                    if type_ in entity_dict:
                        new_value = entity_dict[type_]
                        for p in item["pronoun"]:
                            new_query = new_query.replace(p, new_value)
                if isinstance(type_, (list, tuple)):
                    for t in type_:
                        if t in entity_dict:
                            new_value = entity_dict[t]
                            for p in item["pronoun"]:
                                new_query = new_query.replace(p, new_value)
        new_query = self._question_fill(query)
        return new_query

    def preprocess(self, query, st: State) -> str:
        self.st = st
        new_query = self._clean_pronoun(query)
        return new_query
