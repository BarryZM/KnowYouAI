from core.state import *


class Bot:
    Init = 0

    def __init__(self):
        self.turn = 0  # 多轮对话的一个表示，不需要用户管理,用户可以访问来确定对话是否连续
        self.user_id_table = {}

    def initialization(self):
        # 初始化Bot内的状态机,全部ID都初始化
        for id in self.user_id_table:
            self.user_id_table[id] = Bot.Init


    def check_continue(self, st_turn):
        return self.turn + 1 == st_turn

    def get_response(self, query, st: State):
        raise NotImplemented()

    def helper(self) -> list:
        return []

    def activate_match(self, query, st: State):
        """
        匹配是否主动搭话
        :param query:
        :param st:
        :return:
        """
        return False

    def activate_say(self, query, st) -> str:
        """
        主动搭话，默认是返回帮助信息
        :param query:
        :param st:
        :return:
        """
        return "\n".join(self.helper())

    def match(self, query, st):
        """
        返回匹配是否成功，分数
        :param query:
        :param st:
        :return:
        """
        return False, 0

    def name(self):
        return "Bot<{}>".format(self.__class__.__name__)
