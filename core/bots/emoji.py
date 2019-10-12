from ._base import Bot
from core.state import State
import random
import config
import os


class Emoji(Bot):
    """
    表情包，只作主动搭话
    """

    def __init__(self, dictionary):
        super(Emoji, self).__init__()
        self.dictionary = dictionary

    def activate_match(self, query, st: State):
        ai_sentiment = st.get_ai_sentiment()
        # TODO 根据情绪匹配来决定是否发表情包，并且选择表情包
        # 现在随机匹配
        return random.uniform(0, 1) < 0.2

    def _sentence_with_word(self, seg, sentence):
        """
        setence中是否含有相同的单词
        :param seg:
        :param sentence:
        :return:
        """
        for word, tag in seg:
            if word in sentence and word not in self.dictionary.stop_word:
                return True
        return False

    def activate_say(self, query, st: State):
        if not config.WEIXIN_STYLE:
            return ""
        ai_record = st.get_last_AI_record()
        ai_seg = ai_record.segment
        # ai_response = ai_record.content
        file = [x.path for x in os.scandir(os.path.join(config.EMOJI_PATH, "response")) if any([
            x.path.endswith("jpg"),
            x.path.endswith("jpeg"),
            x.path.endswith("png")
        ])]
        response = []
        for fp in file:
            basename = os.path.basename(fp)
            if self._sentence_with_word(ai_seg, basename):
                response.append("#Image:" + fp)
        if len(response) > 0:
            return random.choice(response)
        else:
            general_emoji = [
                    "#Image:" + x.path for x in os.scandir(os.path.join(config.EMOJI_PATH, "general")) if any([
                        x.path.endswith("jpg"),
                        x.path.endswith("jpeg"),
                        x.path.endswith("png")
                    ])]
            return random.choice(general_emoji)

    def match(self, query, st):
        return False, 0.

    def get_response(self, query, st: State):
        return "我要撩你。"
