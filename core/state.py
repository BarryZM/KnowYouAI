import config
from _global.const import _Speaker, _Sentiment


class Knowledge:
    def __init__(self, common_knowledge, sentence_knowledge):
        self.common_knowledge = common_knowledge
        self.sentence_knowledge = sentence_knowledge


class Record:
    """
    对话窗口中每一条信息的存储格式(文本，其余会通过x2text等方法转成文本)
    """

    def __init__(self, speaker, content, entity, segment, knowledge):
        """

        :param speaker: 说话人身份
        :param content: 内容
        :param entity: 实体
        :param segment: 内容的分词带词性标注
        :param knowledge: 这句话背后的知识  句内的关系（可能实际多跳） 句子实体设计的背景知识（单跳）
        """
        self.speaker = speaker
        self.content = content
        self.entity = entity
        self.segment = segment
        self.knowledge = knowledge


class State:
    """
    全局状态
    记录上下文提及的信息
    以及对话论述
    """

    def __init__(self, user_id):
        # 对话论数
        self.turn = 0
        self.user_id = user_id
        self.callback = None
        # 上下文实体
        self._dialogue_window = []
        self._window_size = config.WINDOW_SIZE
        # AI 当前轮的情感状态
        self._ai_sentiment = _Sentiment.Normal
        # 用户 当前轮的情感状态
        self._user_sentiment = _Sentiment.Normal

    def get_dialogue_window(self):
        return self._dialogue_window

    def set_ai_sentiment(self, sentiment):
        self._ai_sentiment = sentiment

    def set_callback(self,callback):
        self.callback = callback

    def get_ai_sentiment(self):
        return self._ai_sentiment

    def set_user_sentiment(self, sentiment):
        self._user_sentiment = sentiment

    def get_user_sentiment(self):
        return self._user_sentiment

    def add_record(self, speaker, content, entity, segment, knowledge):
        record = Record(speaker, content, entity, segment, knowledge)
        if len(self._dialogue_window) > int(0.8 * self._window_size):
            self._dialogue_window = self._dialogue_window[-int(0.5 * self._window_size):]
        self._dialogue_window.append(record)

    def get_last_AI_record(self) -> Record:
        """
        获得最新的AI回复
        :return:
        """
        item = None
        for elem in self._dialogue_window[::-1]:
            if not isinstance(elem, Record):
                continue
            if elem.speaker == _Speaker.AI:
                item = elem
                break
        return item

    def get_AI_ever_say(self) -> list:
        """
        获得历史的AI回复，纯文本
        :return:
        """
        result = []
        for elem in self._dialogue_window[::-1]:
            if not isinstance(elem, Record):
                continue
            if elem.speaker == _Speaker.AI:
                result.append(elem.content)
        return result

    def get_last_User_record(self) -> Record:
        """
        获得最新的用户回复
        :return:
        """
        item = None
        for elem in self._dialogue_window[::-1]:
            if not isinstance(elem, Record):
                continue
            if elem.speaker == _Speaker.USER:
                item = elem
                break
        return item
