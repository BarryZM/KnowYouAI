from ._base import Bot
from core.state import State
from _global import regex
from _global.const import _Score


class System(Bot):
    """
    访问system信息
    """

    def __init__(self, pool, eval_tool):
        super(System, self).__init__()
        self.pool = pool
        self.eval_tool = eval_tool
        # self.eval_tool.register(name="test", callback_get_params=lambda: {"score": 100}, template="评估分数:{score}")

    def match(self, query, st):
        """

        :param query:
        :param st:
        :return:
        """
        flag = regex.system_resource1.search(query) or regex.system_resource2.search(query) or \
               regex.system_ability.search(query)
        score = _Score.LevelLow if flag else 0.
        return flag is not None, score

    def get_response(self, query, st: State):
        if any([regex.system_resource1.search(query), regex.system_resource2.search(query)]):
            pool_size = self.pool.pool_size
            curr_pool = self.pool.running_mission_number
            line = ["System Resource:", "PoolSize:{}".format(pool_size), "Curr Mission:{}".format(curr_pool)]
            for i, name in enumerate(self.pool.running_mission_name):
                line.append("[{id}]-{name}".format(id=i + 1, name=name))
            line.append("Info {} item".format(self.pool.info_queue.qsize()))
        else:
            line = self.eval_tool.get_eval()
        return "\n".join(line)
