from _global import global_logger
from _global.const import _Topic
import config
import os
import config
import time
import glob
from py2neo import walk


class EntityObj:
    def __init__(self, type_, entity, pros, topic):
        self._type = type_ or []  # list
        self._entity = entity  # str
        self._pros = pros or ["这"]  # list
        self._topic = topic or []  # list

    @property
    def type(self) -> list:
        return self._type

    @property
    def entity(self) -> str:
        return self._entity

    @property
    def pros(self) -> list:
        return self._pros

    @property
    def topic(self) -> list:
        return self._topic

    def to_dict(self):
        return {
            "type": self.type,
            "entity": self.entity,
            "pros": self.pros,
            "topic": self.topic
        }

    @staticmethod
    def from_dict(dict):
        return EntityObj(dict["type"], dict["entity"], dict["pros"], dict["topic"])

    def __repr__(self):
        return "EntityObj(type={} entity={} pros={} topic={})".format(
            self.type, self.entity, self.pros, self.pros
        )


class EntityTool:
    def __init__(self, global_KG, text_tool):
        self.graph = global_KG.getInstance(config.NEO4F_CONF)
        # 缓存起来所有实体
        # 连key value都要缓存起来才能快，因为是生成器每次迭代都要问一次server?
        # 以后达到一定数目再调优
        self.entity_name_set = set()
        self.entity_word = []
        self.entity_word_from_net = self._load_entity_from_txt()  # 这里的实体有属性值，优先保留
        for node in self.graph.run("match (n:entity) return n"):
            value = node[0]["value"]
            if value not in self.entity_name_set:
                self.entity_name_set.add(value)
                self.entity_word.append({
                    "value": value,
                    "label": [],  # list
                    "pros": ["这"],  # list
                    "topic": []  # list
                })
        global_logger.info("Buffer the entity word from KG:{} from Net:{}".format(len(self.entity_word),
                                                                                  len(self.entity_word_from_net)))
        self.text_tool = text_tool

    def _load_entity_from_txt(self):
        # file = [x.path for x in os.scandir(config.LEARN_PATH) if x.path.endswith("entity.txt")]
        file = glob.glob(os.path.join(config.LEARN_PATH, "*/*_entity.txt")) + glob.glob(
            os.path.join(config.ENTITY_PATH, "*.txt"))
        visit = {}
        result = []
        for fp in file:
            for line in open(fp, "r", encoding="utf-8"):
                line_list = line.strip().split("|")
                if len(line_list) != 4:
                    continue
                if line_list[0] in visit:
                    continue
                # 纠正一下学习文本时错误
                label = [(lab if lab != "people" else _Topic.People) for lab in line_list[1].split(",")]
                topic = [(top if top != "people" else _Topic.People) for top in line_list[3].split(",")]
                data = {
                    "value": line_list[0],
                    "label": label,  # list
                    "pros": line_list[2].split(","),  # list
                    "topic": topic  # list
                }
                visit[data["value"]] = 1
                self.entity_name_set.add(data["value"])
                result.append(data)
        return result

    def extract(self, query, state=None, dynamic=False):
        """
        返回一个list,每个元素是个dict有个两个字段
        entity
        type
        :param query
        :param state 上下文 必要时消除歧义(如李白，人名，歌曲名)，一般为None
        :param dynamic 是否'动态'载入文件版的实体记录
        :return:({"type": type_, "entity": entity, "pros": pros, "topic": topic})
            pros list
            type_ list
            topic list
            entity str
        """
        t1 = time.time()
        result = []
        query_seg = self.text_tool.lcut(query)  # 先进行分词，避免词和子词都识别出来了
        # print(query_seg)
        if dynamic:
            entity_word_from_net = self._load_entity_from_txt()
        else:
            entity_word_from_net = self.entity_word_from_net
        for node in entity_word_from_net:
            entity = node["value"]
            type_ = node["label"]
            pros = node["pros"]  # 该实体的代词形势
            topic = node["topic"]
            if entity in query_seg:
                entity_obj = EntityObj(type_, entity, pros, topic)
                result.append(entity_obj)
        for node in self.entity_word:
            entity = node["value"]
            type_ = node["label"]
            pros = node["pros"]  # 该实体的代词形势
            topic = node["topic"]
            if entity in query_seg:
                entity_obj = EntityObj(type_, entity, pros, topic)
                result.append(entity_obj)
        global_logger.info("Cost Time:{:.2f} query:{} entity:{}".format(time.time() - t1, query, result))
        return result

    def get_relation_ship_by_entity(self, entity_items: list):
        """
        抽取列表内的每一个实体的所有关系（可以是中文）
        :param entity_items:
        :return:
        """
        # TODO 考虑更大的知识图谱或网络知识图谱
        relations = {}
        for entity_item in entity_items:
            if not isinstance(entity_item, EntityObj):
                continue
            result = []
            cy = "match (p)-[r]->(p1) where p.value = \"{name}\" return p, r,p1".format(name=entity_item.entity)
            try:
                rs = self.graph.run(cy)
            except Exception as e:
                rs = []
                global_logger.info("cy execute error.{}".format(cy))
            for r in rs:
                result.append((r[1]["value"], r[2]["value"]))
            relations[entity_item.entity] = result
        return relations

    def relationship_with_entity(self, entity_objA: EntityObj, entity_objB: EntityObj, max_jump=3):
        """
        两个实体之间的关系
        允许多跳查找
        允许反向查找
        :param entity_objA:
        :param entity_objB:
        :param max_jump : 节点之间最大的关系跳数
        :return:
        """
        cy = "match path=(p)-[*..{max_jump}]->(p1)  where p.value = \"{p1}\" and p1.value=\"{p2}\"   return path"
        temp = cy.format(max_jump=max_jump, p1=entity_objA.entity, p2=entity_objB.entity)
        # global_logger.info("fuck:{}".format(temp))
        try:
            exec_result = self.graph.run(temp)
        except Exception as e:
            exec_result = []
            global_logger.info("cy execute error.{}".format(temp))
        exec_result = list(exec_result)
        if len(exec_result) == 0:
            try:
                temp = cy.format(max_jump=max_jump, p1=entity_objB.entity, p2=entity_objA.entity)
                exec_result = self.graph.run(temp)
            except Exception as e:
                exec_result = []
                global_logger.info("cy execute error.{}".format(cy))
        result = []
        for path_record in exec_result:
            path_list = []
            for p in walk(path_record[0]):
                path_list.append(p["value"])
            result.append(path_list)
        return result
