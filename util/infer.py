import config


class Infer:
    def __init__(self, graph):
        # self.config = config
        self.graph = graph.getInstance(config.NEO4F_CONF)
        self.relationship_keyword = {
            "朋友": "friend"
        }

    def similar_entity(self, entity_list_from_st: list, rules: [dict]) -> list:
        """
        根据entity_list找到相似的实体
        :param entity_list_from_st:
        :param rules [dict],type是类型，rulu是一条关系查询语句 (若需要在可在图的起点有{value}占位符 )找到的全返回 ，
                            查询返回的是一个列表，每一项选中的索引为index
        :return: # [dict] key：type:对应的实体类型 reuslt：根据rule找回来的答案(列表) 特殊的key pros是这段谈话的主体的代词
        """
        result_dict = []
        for entity in entity_list_from_st:
            type = entity["type"]
            value = entity["entity"]
            pros = entity["pros"]
            # 找针对这类型规则（查询的关系）
            rule_result = {
                'type': type,
                'pros': pros,
                'result': []
            }
            if isinstance(type, (list, tuple)):
                for t in type:
                    if t in rules:
                        cypher = rules[t].replace("{value}", value)
                        index = rules['index']
                        result = self.graph.run(cypher)
                        for res in result:
                            rule_result['result'].append([res[i] for i in index])
                        if len(rule_result['result']) > 0:
                            result_dict.append(rule_result)
            elif isinstance(type, str):
                t = type
                if t in rules:
                    cypher = rules[t].replace("{value}", value)
                    index = rules['index']
                    result = self.graph.run(cypher)
                    for res in result:
                        rule_result['result'].append([res[i] for i in index])
                    if len(rule_result['result']) > 0:
                        result_dict.append(rule_result)

        return result_dict

    def get_detail_Realation(self, entity, attr, cypher):
        """
        查询实体的直接关系的实体（Node对象）
        :param entity:
        :param attr:
        :return:
        """
        # 获取关系名称
        relationship = ""
        for keyword in self.relationship_keyword:
            if keyword in attr:
                relationship = self.relationship_keyword[keyword]
                break
        if relationship == "":
            return []
        else:
            cypher = cypher.format(entity=entity, relationship=relationship)
            result = self.graph.run(cypher)
            return [res[0] for res in result]
