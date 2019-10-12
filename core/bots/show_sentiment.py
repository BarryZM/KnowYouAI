from ._base import Bot
from core.state import State
from _global.const import _Sentiment
import random


class ShowSentiment(Bot):
    """
    表达情绪
    """
    # TODO 以后考虑用强化学习来判断是否表达情绪
    def __init__(self, ai_being):
        super(ShowSentiment, self).__init__()
        self.ai_being = ai_being

    def activate_match(self, query, st):
        # 一定概率表达自己的心情
        relationship = self.ai_being.get_value("relationship", st.user_id) / 100

        return random.uniform(0, 1) < relationship * 0.2

    def activate_say(self, query, st: State):
        ai_sentiment = st.get_ai_sentiment()
        if ai_sentiment == _Sentiment.Positive:
            ans = random.choice(
                [
                    "开心心",
                    "{},我现在心情不错噢".format(self.ai_being.get_value("your_name", st.user_id)),
                    "啦啦啦"
                ],
            )
        elif ai_sentiment == _Sentiment.Negative:
            ans = random.choice(
                [
                    "坏人，我不开心了",
                    "不开心",
                    "不允许骂人"
                ]
            )
        else:
            ans = random.choice(
                [
                    "{},今天心情一般般啦".format(self.ai_being.get_value("your_name", st.user_id)),
                    "今天过得还行"
                ]
            )
        return ans

    def match(self, query, st):
        """
        不被动匹配
        :param query:
        :param st:
        :return:
        """
        return False, 0

    def get_response(self, query, st: State):
        return ""
