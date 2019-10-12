from ._base import Bot
from core.state import State
from core.nlg import NLG
import random
import config
import gensim
import sqlite3
import json


class _Result:
    def __init__(self, qid, title, topic, aid, segment):
        self.qid = qid
        self.title = title
        self.topic = topic
        self.aid = aid
        self.segment = segment

    def to_url(self):
        url = "https://www.zhihu.com/question/{qid}/answer/{aid}".format(qid=self.qid, aid=self.aid)
        return url

    def __repr__(self):
        return "Result(qid={qid},title={title},topic={topic},aid={aid} segment={segment})".format(
            qid=self.qid,
            title=self.title,
            topic=self.topic,
            aid=self.aid,
            segment=self.segment
        )


class Chat(Bot):
    """
    情景导向闲聊
    某个情景对应一个关键词（agent intent），agent引导user走向这个关键词，最后当用户或者agent说出这个关键词视为完成
    完成时可以触发进一步的动作
    这个是1.0-2.0版本的主要框架

    """
    # 1.1 情景1 通过聊天引导去一个cQA的连接
    # TODO 更多的情景，
    # 比如土味情话，比如 引导用户分享特别的个体的事情，用户喜欢的名词作为目标词,询问用户一些事情等
    # 将情景抽象出来
    # TODO 更好的话题概率转移模型，和转移路径的相关计算
    # TODO 更好的解决一些N选1的问题，比如N个agent intent和N个推荐信息,N个字符中挑选target word（先挑选tf-idf最大的,
    # 后面可以引入主题词，对cQA 文本进行搜索）
    Wait = 1  # 处于引导状态中

    def __init__(self, dictionary, ai_being, user_profile, logger, ask, text_tool):
        super(Chat, self).__init__()
        # TODO 换更好，更快，更小的embedding
        self.word2vector = gensim.models.KeyedVectors.load(config.WORD2VECTOR_PATH, mmap='r')
        self.tf_idf = json.load(open(config.TF_IDF_PATH, "r", encoding="utf-8"))
        self.nlg = NLG(dictionary, ai_being, user_profile, logger, ask, text_tool, self.word2vector, self.tf_idf)
        self.cqa_database = sqlite3.connect(config.CQA_PATH, check_same_thread=False)
        self.logger = logger
        self.user_id_agent_target = {}  # 目标场景的关键词
        # 情景一任务相关
        self.user_id_Record = {}  #
        self._recomand_url_say = [
            "推荐给你看看",
            "看看这个链接",
            "你可以看看这个"
        ]
        ####
        self.dictionary = dictionary
        self.text_tool = text_tool
        self._next_sentence_threshold = 0.8  # 转移概率wj->wi超过这个值，即认为是可以转移
        self._change_topic_threshold = 0.25  # 全部候选词转移概率wj->wi低于这个值，即认为是已经谈及新的话题

    def _is_next(self, wj, wi):
        """
        用一个话题转移模型来判断wj->wi的概率
        :param word1:
        :param word2:
        :return:
        """
        # PMI log(P(wi|wj)/p(wi))
        # v1 基于word2vector做
        if wj not in self.word2vector or wi not in self.word2vector:
            return 0
        score = self.word2vector.similarity(wj, wi)
        return score

    def _get_embedding_similarity_words(self, word):
        """
        获取word在转移模型上的前置(名词)
        :param word:
        :return:
        """
        result = self.word2vector.most_similar(positive=word, topn=10)
        similarity_word = [word for word, _ in result]
        return similarity_word

    def _is_next_sentence(self, keyword: list, target_word: str):
        """
        判断target_word 能否在含有keyword的句子的下一句出现
        :param keyword:
        :param target_word:
        :return:
        """
        for word in keyword:
            score = self._is_next(word, target_word)
            if score >= self._next_sentence_threshold:
                return True
        return False

    def _next_word(self, keyword: list, target_similarity: list):
        """
        在target_similarity找到最符合keyword的下一个词
        :param keyword:
        :param target_similarity:
        :return:
        """
        max_score = 0
        target_word = ""
        for similarity_word in target_similarity:
            for word in keyword:
                score = self._is_next(word, similarity_word)
                if score > max_score:
                    max_score = score
                    target_word = similarity_word
        if max_score < self._change_topic_threshold:
            return None
        return [target_word]

    def _init_user_id_state(self, user_id):
        """
        初始化user id相关的上下文信息
        :param user_id:
        :return:
        """
        self.user_id_table[user_id] = Chat.Init
        self.user_id_agent_target[user_id] = None
        # 情景一任务相关
        self.user_id_Record[user_id] = None

    def _get_key_word_id(self, st: State):
        user_record = st.get_last_User_record()
        # 采用分词而不是实体来做keyword
        IDS = set()
        keyword = []
        for i, (word, tag) in enumerate(user_record.segment):
            if "nr" == tag and len(word) == 1 and (i + 1) > len(user_record.segment):
                w, _ = user_record.segment[i + 1]
                name = word + w
                keyword.append(name)
            elif "n" in tag:
                keyword.append(word)
        for entityobj in user_record.entity:
            keyword.append(entityobj.entity)
        if len(keyword) == 0:
            keyword.append(user_record.content)
        condition_sql = "or".join([" instr({}, '{}') > 0 ".format("KEYWORD", key) for key in keyword])
        sql = "select KEYWORD,ID_LIST from cQA_index where {}".format(condition_sql)
        result = self.cqa_database.execute(sql)

        for row in result:
            ids = row[1].split(",")
            for id in ids:
                IDS.add(id)
        return IDS

    def _get_ans_by_id(self, ids):
        if len(ids) > 100:
            ids = random.sample(ids, k=100)
        R = []
        if len(ids) == 0:
            return R
        condition_sql = "or".join([" ID={} ".format(id) for id in ids])
        # print(condition_sql)
        sql = "select ID,Q_ID,TITLE,TOPIC,A_ID from cQA_pair where {}".format(condition_sql)
        result = self.cqa_database.execute(sql)

        for row in result:
            result_item = _Result(qid=row[1], title=row[2], topic=row[3], aid=row[4],
                                  segment=self.text_tool.pos_lcut(row[2]))
            R.append(result_item)
        return R

    def _select_target_word(self, content, keyword):
        """
        在content中找合适的target word 并且不与keyword重合
        :param content:
        :return:
        """
        seg = self.text_tool.pos_lcut(content)
        seg = [word for word, tag in seg
               if word not in self.dictionary.stop_word and ("n" in tag or "v" in tag) and len(word) > 1]
        max_score = 0
        target_word = None
        for word in seg:
            score = self.tf_idf.get(word, 0)
            if score > max_score and word not in keyword and word in self.word2vector:
                max_score = score
                target_word = word

        return target_word

    def _find_next_word(self, query, keyword, target_word):
        """
        检测target是否作为下一句输出，否则找出下一个targetword
        :param query:
        :param keyword:
        :param target_word:
        :return:
        """
        # print("Fuck",target_word,query)
        if target_word in query or self._is_next_sentence(keyword, target_word):
            return [target_word]
            # 开始找判断场景是否转移，推进话题
        similarity_word = self._get_embedding_similarity_words(target_word)
        next_word = self._next_word(keyword, similarity_word)
        return next_word

    def _parse_query(self, query, st: State, call_self=True):
        """
        对用户的query进行解释处理
        实体 = 分词中长度大于1的名词
        1. 初始状态中 没有实体的话语 -变成普通的闲聊回答
        2. 转移过程中 没有实体的话语 -让agent自己继续场景
        3. 能检测出实体，但没有预设好对应场景
        4. 谈话中，场景发生变化
        5 正常谈话中 检测出内容词 （在场景1中就是找到一个可以推荐的cQA连接）

        情景完成后返回的列表中含有target word
        :param query:
        :param st:
        :param call_self ：是否可以调用自己
        :return: list 下一句话期待的target word
        """
        state = self.user_id_table[st.user_id]
        user_record = st.get_last_User_record()
        seg = [word for word, tag in user_record.segment
               if word not in self.dictionary.stop_word and ("n" in tag or "v" in tag) and len(word) > 1]
        keyword = seg
        # print(keyword)
        if state == Chat.Init:
            if len(keyword) == 0:
                # 等价于无意义的闲聊
                return None
            else:
                # 开始找合适场景
                # 在场景1中就是找到一个可以推荐的cQA连接
                ids = self._get_key_word_id(st)
                result_items = self._get_ans_by_id(ids)
                # n个样本最多采样n次，都找不到关键词就变成普通闲聊了
                random.shuffle(result_items)  # 先随机打乱顺序
                for item in result_items:
                    target_word = self._select_target_word(item.title, keyword)

                    if target_word:
                        # url = item.to_url()
                        print("Find the target word:", target_word)
                        self.user_id_Record[st.user_id] = item
                        self.user_id_agent_target[st.user_id] = target_word
                        next_word = self._find_next_word(query, keyword, target_word)
                        self.user_id_table[st.user_id] = Chat.Wait
                        return next_word
                return None

        elif state == Chat.Wait:
            target_word = self.user_id_agent_target[st.user_id]
            print("New turn target word", target_word)
            if len(keyword) == 0:
                # 完全靠agent来引导话题,如用户在说，哈哈哈。好厉害这种
                # 这时的keyword改成ai的上一句
                ai_record = st.get_last_AI_record()
                seg = [word for word, tag in user_record.segment
                       if word not in self.dictionary.stop_word and ("n" in tag or "v" in tag) and len(word) > 1]
                keyword = ai_record.entity or seg
                # 开始判断是否已经达成目标
            next_word = self._find_next_word(query, keyword, target_word)
            if not next_word:
                # 没法找到下一个word 用户转移话题
                self._init_user_id_state(st.user_id)
                # 递归调用
                if call_self:
                    next_word = self._parse_query(query, st, False)  # 新话题尝试一次，防止无限递归
                return next_word
            return next_word
        else:
            raise ValueError("[user_id:{}] Unknown state: {}  query:{}".format(st.user_id, state, query))

    def get_response(self, query, st: State):
        if st.user_id not in self.user_id_table:
            # 第一次访问
            self._init_user_id_state(user_id=st.user_id)
        keyword = self._parse_query(query, st)
        assert (isinstance(keyword, list)) or (keyword is None), \
            "keyword type:{} value:{}".format(type(keyword), keyword)
        if not keyword:
            # 变成了闲聊，AI 应该主动引导回话题
            pass
        ans = self.nlg.get_response(query, st, keyword=keyword, keyword_priorty=True)
        target_word = self.user_id_agent_target[st.user_id]
        self.logger.info("state:{} query:{} parsed-keyword(next):{} target_word:{}".format(
            self.user_id_table[st.user_id], query, keyword, target_word))
        finish = False
        if target_word:
            if target_word in ans:
                finish = True
            if keyword and target_word in keyword:
                finish = True
        if finish:
            # do something
            say = random.choice(self._recomand_url_say)
            record = self.user_id_Record[st.user_id]
            ans += "\n{}：{} {}".format(say, record.title, record.to_url())
            # 任务完成
            self._init_user_id_state(user_id=st.user_id)
        # print("Finish targetword", target_word)
        return ans
