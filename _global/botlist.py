from core.bots import Bot, Chat
import config
from core.state import State
from .logging import global_logger
import random


class BotList:
    def __init__(self, bots, image_bot, default_chat_bot: Bot):
        self.bots = bots + image_bot
        # 默认的default bot
        self.chat_bot = default_chat_bot
        self.image_bot = image_bot

    def initialization(self):
        for bot in self.bots:
            if isinstance(bot, Bot):
                bot.initialization()

    def get_bot_remind(self, query, st):
        """
        每一个小bot都有一个关键词，
        当提及这个关键词时，框架会调用用户的回调函数
        主动提醒用户可以通过某个语句唤醒某个小bot
        提醒信息来自bot的helper函数
        也可以作为主动搭话的机制，为了避免消息拥堵，每次只能一个小bot主动提醒一次，随机选择
        :return:
        """
        infos = []
        for bot in self.bots:
            if isinstance(bot, Bot) and bot.activate_match(query, st):
                say = bot.activate_say(query, st)
                if say:
                    infos.append(say)
        if len(infos) > 0:
            info = random.choice(infos)
        else:
            info = ""
        return info

    def match(self, query, st: State) -> Bot:
        """
        匹配合适的bot回来
        :param query:
        :param st:
        :return:
        """
        min_score = config.THRESHOLD_BOT
        select_bot = self.chat_bot
        for bot in self.bots:
            if isinstance(bot, Bot):
                flag, score = bot.match(query, st)
                global_logger.info("{} match:{} score:{}".format(bot.name(), flag, score))
                if flag and score > min_score:
                    min_score = score
                    # 被抢夺的bot回归初始状态（起到切换bot）
                    # select_bot.initialization(st.user_id)
                    select_bot = bot
        return select_bot

    def match_image_bot(self, query, st: State) -> Bot:
        """
        匹配合适的bot回来
        :param query:
        :param st:
        :return:
        """
        min_score = config.THRESHOLD_BOT
        select_bot = None
        for bot in self.image_bot:
            if isinstance(bot, Bot):
                flag, score = bot.match(query, st)
                global_logger.info("{} match:{} score:{}".format(bot.name(), flag, score))
                if flag and score > min_score:
                    min_score = score
                    # 被抢夺的bot回归初始状态（起到切换bot）
                    # select_bot.initialization(st.user_id)
                    select_bot = bot
        return select_bot

    def get_help(self) -> str:
        helps = []
        for bot in self.bots:
            if isinstance(bot, Bot):
                helper = bot.helper()
                helps.extend(helper)
        if len(helps) > config.MAX_HELP:
            helps = random.sample(helps, config.MAX_HELP)
        return "\n".join(helps)
