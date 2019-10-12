
# 知识图谱工具
from py2neo import Graph, Node
from py2neo import Relationship as RelationshipNEO
class GlobalKG:

    def __init__(self):
        self._host_instance = {

        }

    def getInstance(self,sub_conf)->Graph:
        url =sub_conf["url"]
        if url not in self._host_instance:
            self._host_instance[url] = Graph(url, username=sub_conf["username"], password=sub_conf["password"])
        return self._host_instance[url]