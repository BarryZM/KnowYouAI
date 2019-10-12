from core.state import State
import random
from _global.const import _Sentiment
import json
import config
from _global import regex
import util
import os
from core.nn import Matcher, get_w2i4matchnet, cut_word4matchnet
import gensim
import sqlite3


class NLG:
    # TODO 让user profile和AI profile更好的决定输出

    def __init__(self, dictionary, ai_being, user_profile, logger, ask, text_tool, word2vector,tf_idf):
        self.dictionary = dictionary
        self.ai_being = ai_being
        self.user_profile = user_profile
        self.tf_idf = tf_idf
        self.logger = logger
        self.database = sqlite3.connect(config.POST_RESPONSE_PATH, check_same_thread=False)

        self.word2vector = word2vector
        self.w2i = get_w2i4matchnet(config.MATCH_W2I_PATH)
        self.matcher = Matcher(len(self.w2i), 256)
        self.matcher.load(config.MATCH_CHECKPOINT)
        self.ask = ask
        self.text_tool = text_tool
        self.default_candidate = [
            "继续继续",
            "不知道该说什么了。",
            "让我组织组织语言，突然不知道该怎么说了",
            "我懵逼了",
            "我伸个懒腰再跟你聊天，继续刚刚的话题",
            "容我想想",
            "emmmmmm...."
        ]

    """
    Common method
    """

    def _check_ai_profile(self, candidates: list, user_id):
        """
        对候选答案进行计算分数，检测和ai profile的差距
        :param candidates:
        :return:
        """
        new_candidate = []
        key_list = [key for key in self.ai_being.get_key(user_id)]
        like_score = 1.  # 喜欢的话得分是score
        for candidate in candidates:
            if isinstance(candidate, str):
                can = candidate
            elif isinstance(candidate, dict):
                can = candidate["response"]
            else:
                continue
            for key in key_list:
                if "like" in key:
                    item = self.ai_being.get_value(key, user_id)
                    if isinstance(item, str):
                        if item in can:
                            new_candidate.append({"response": can, "weight": like_score})
                        else:
                            new_candidate.append({"response": can, "weight": like_score * 0.9})
                    elif isinstance(item, (list, tuple)):
                        flag = False
                        for it in item:
                            if it in can:
                                flag = True
                                new_candidate.append({"response": can, "weight": like_score})
                                break
                        if not flag:
                            new_candidate.append({"response": can, "weight": like_score * 0.9})
                    else:
                        continue
        return new_candidate

    def get_score_by_rank(self, idx, total):
        """
        根据排名获取分数
        :param idx: 物理位置
        :param total: 总长
        :return:
        """
        sup = total - idx  # 超越了多少名次，使用物理位置是为了最后一名不至于为0分
        score = sup / total
        return score

    def _command_word(self, query):
        """
        命令的句子，疑问句等
        在检测用户说过的句子时不允许使用
        :return:
        """
        for command in regex.command:
            if command.search(query):
                return True
        return False

    def _dropout(self, items):
        """

        :param items: key-value  response回答 按照weight丢掉一些样本，从而实现按照一定的权重来随机选择
        :return:
        """
        new_candidate = []
        for item in items:
            response = item["response"]
            weight = item["weight"]
            if random.uniform(0, 1) < weight:
                new_candidate.append(response)
        return new_candidate

    def _get_sentence_vector(self, keyword, mean=True):
        vector = 0.
        for word in keyword:
            if word in self.word2vector:
                vector += self.word2vector[word]
            else:
                vector += self.word2vector["<UNK>"]
        if mean:
            vector = vector / len(keyword)
        return vector

    def _has_ban(self, sentence):
        for word in self.dictionary.ban_word:
            if word in sentence:
                return True
        return False

    def _match_score(self, query, response):
        """
        语义匹配


            :param query:用户的query
            :param response: 候选回答
            :return:
            """
        max_len = 20
        query_idx = [(self.w2i[word] if word in self.w2i else self.w2i['<UNK>']) for word in
                     cut_word4matchnet(query)]
        if len(query_idx) > max_len:
            query_idx = query_idx[:max_len]
        else:
            query_idx = query_idx + [self.w2i["<PAD>"] for _ in range(max_len - len(query_idx))]
        response_idx = [(self.w2i[word] if word in self.w2i else self.w2i['<UNK>']) for word in
                        cut_word4matchnet(response)]
        if len(response) > max_len:
            response_idx = response_idx[:max_len]
        else:
            response_idx = response_idx + [self.w2i["<PAD>"] for _ in range(max_len - len(response_idx))]
        score = self.matcher.get_score([query_idx], [response_idx])

        return score

    """
    No Scene Begin
    """

    def _read_doc_no_scene(self, user_id):
        """

        :return: list [str]
        """
        # ai_like_topic = personal.character.character["like_topic"]
        dir_ = os.path.join(config.LEARN_PATH, user_id)
        paths = [x.path for x in os.scandir(dir_) if x.path.endswith("_begin.txt")]
        candidata_ans = []
        pattern = regex.pro_re  #
        for path in paths:
            for sentence in open(path, "r", encoding="utf-8"):
                sentence = sentence.strip()
                result = regex.new_topic_being.search(sentence)
                if result is not None and "我" not in sentence:
                    # 改写一下，再加入
                    begin = result.span()[0]
                    sentence = sentence[begin:]
                    sentence = pattern.sub("某人", sentence)
                    # 判断是否有动词，可以一定程度上判断句子是否合法
                    if len(sentence) > 5 and self._has_v(sentence):
                        # 改了后不能太短
                        candidata_ans.append(sentence)
        return candidata_ans

    def _has_v(self, sentence):
        """
        检测句子是否含动词
        :param sentence:
        :return:
        """
        seg = self.text_tool.pos_lcut(sentence)
        for word, tag in seg:
            if tag == "v":
                return True
        return False

    def _read_pair_data_no_sence(self, query):
        # 因为已经不考虑实体了，所以直接用query是否含有pair的关键词就行了，情感要进一步进行
        # TODO 使用文件检索引擎来处理这部份数据的读写
        self._sentiment_tag = {
            "negative": _Sentiment.Negative,
            "normal": _Sentiment.Normal,
            "positive": _Sentiment.Positive
        }
        result = []
        file = [x.path for x in os.scandir(os.path.join(config.PAIR_DIR)) if x.path.endswith("txt")]
        visit = []
        for fp in file:
            for line in open(fp, "r", encoding="utf-8"):
                item_list = line.strip().split("####")
                if len(item_list) != 3:
                    continue
                key_word, response, sentiment = item_list
                sentiment = self._sentiment_tag[sentiment]
                if key_word in query and response not in visit:
                    visit.append(response)
                    result.append({"response": response, "weight": 1, "sentiment": sentiment})
        return result

    def _no_scene(self, query, st) -> str:
        candidate_finall = []
        candidate_lv2 = []
        ai_sentiment = st.get_ai_sentiment()
        # 读取say的
        # 没有检测出实体的，可能合适维持聊天的回复
        visit = []
        path = "./UserData/{user_id}/say.txt".format(user_id=st.user_id)
        for line in open(path, "r", encoding="utf-8"):
            parsed_json = json.loads(line.strip())
            # 回答不含实体的一般都不含实际情景
            resp = parsed_json["response"]
            sentiment = parsed_json["response_sentiment"]
            if len(parsed_json["response_entity"]) == 0 \
                    and not self._has_ban(resp) \
                    and resp not in visit \
                    and resp != query and not self._command_word(resp):
                # 没有实体，太长也不行。因为太长了，可能时有实体，但没检测出来
                length = len(resp)
                max_length = 6
                length_limit = 10
                alpha = (length - max_length) / (length_limit - max_length)
                weight = 1 if len(resp) <= max_length else max(0, 1 - alpha)
                candidate_lv2.append({"response": resp, "weight": weight, "sentiment": sentiment})
                # candidate_lv2.append(resp)
                visit.append(resp)
        # 情感过滤
        candidate_lv3 = []
        for candidate in candidate_lv2:
            if ai_sentiment == _Sentiment.Negative and ai_sentiment == candidate["sentiment"]:
                candidate_lv3.append(candidate)
            if ai_sentiment != _Sentiment.Negative and candidate["sentiment"] != _Sentiment.Negative:
                candidate_lv3.append(candidate)
        """
        根据score来排队，大于T的保留下来，
        为了处理与存在scene（含有实体）但没有被检测出来的句子
        然后根据队伍位置赋值权重，dropout一次再产生一次候选队列
        """
        temp = []
        for item in candidate_lv3:
            response = item["response"]
            score = self._match_score(query, response)
            if score > config.MATCH_THRESHOLD:
                item["weight"] = score
                temp.append(item)
        temp = sorted(temp, key=lambda item: item["weight"], reverse=True)
        # 根据排名更新权值
        candidate_lv3 = [
            {"response": item["response"], "weight": self.get_score_by_rank(i, len(temp))}
            for i, item in enumerate(temp)]
        candidate_finall.extend(self._dropout(candidate_lv3))
        # 无实体的pair data 不考虑语义匹配，情绪匹配后直接进入最后的候选队列
        # 读取pair
        pair_data = self._read_pair_data_no_sence(query)
        for candidate in pair_data:
            if ai_sentiment == _Sentiment.Negative and ai_sentiment == candidate["sentiment"]:
                candidate_finall.append(candidate["response"])
            if ai_sentiment != _Sentiment.Negative and candidate["sentiment"] != _Sentiment.Negative:
                candidate_finall.append(candidate["response"])
        """
        没有答案就引导新话题
        """
        if len(candidate_finall) == 0:
            candidate_finall.extend(self._read_doc_no_scene(user_id=st.user_id))
        ai_ever_say = st.get_AI_ever_say()
        candidate_finall = [resp for resp in candidate_finall if resp not in ai_ever_say]
        """
        啥手段都没有就默认回答
        """
        if len(candidate_finall) == 0:
            candidate_finall.extend(self.default_candidate)
        # no scene的不需要语义匹配和排序，都是些增加conversion smooth的通用回复
        self.logger.info("No scene candidate ans:{}".format(candidate_finall))
        return random.choice(candidate_finall)

    """
    No Scene End
    """
    """
    Scene Begin
    """

    def _rerank_topic(self, keyword, candidates):
        """
        对候选进行topic 排序
        当一句话的主题词出现topic A topic B *n时，候选匹配会偏向topic B，但实际语境不一定
        比如GIT 真是合适一个菜鸡和傻逼的功具。实际人家是在谈GIT，而不是菜鸡和傻逼
        :param candidates:
        :return:
        """
        # V1 使用tf-idf 在所有topic词中最大的那个作为整个句子的topic，然后用候选回答的平均词向量到topic词的平均向量来排序
        # TODO 更多的特征,比如主题模型
        max_score = 0
        new_rank = []
        topic_word = keyword[0]
        for word in keyword:
            if word in self.tf_idf:
                score = self.tf_idf[word]
                if score > max_score:
                    max_score = score
                    topic_word = word
        if topic_word not in self.word2vector:
            # 无法进行下列比较
            return candidates
        key_vector = self.word2vector[topic_word]
        for candidate in candidates:
            can = candidate
            weight = 1.  # 该句子之前的得分
            if isinstance(candidate, dict):
                can = candidate["response"]
                weight = candidate.get("weight", 1)  # 更新一下分数
            can_keyword = [word for word, _ in self.text_tool.pos_lcut(can) if
                           word not in self.dictionary.stop_word]
            can_vector = self._get_sentence_vector(can_keyword)
            size = key_vector.shape[0]
            score = util.cos_distance(key_vector.reshape((size, 1)), can_vector.reshape((size, 1)))
            score = score * weight
            new_rank.append({"response": can, "weight": score})
        return new_rank

    def _read_user_say_data_sence(self, keyword: list, st: State, n=10):
        visit = []
        candidate = []
        if len(keyword) == 0:
            return []
        key_vector = self._get_sentence_vector(keyword)
        path = "./UserData/{user_id}/say.txt".format(user_id=st.user_id)
        for line in open(path, "r", encoding="utf-8"):
            parsed_json = json.loads(line.strip())
            # 回答不含实体的一般都不含实际情景
            resp = parsed_json["response"]
            sentiment = parsed_json["response_sentiment"]
            if len(parsed_json["response_entity"]) != 0 \
                    and not self._has_ban(resp) \
                    and resp not in visit:
                cand_keyword = [word for word, _ in self.text_tool.pos_lcut(resp) if
                                word not in self.dictionary.stop_word]
                if len(cand_keyword) > 0:
                    cand_vector = self._get_sentence_vector(cand_keyword)
                    if isinstance(cand_vector, float) or isinstance(key_vector, float):
                        score = 0
                    else:
                        size = key_vector.shape[0]
                        score = util.cos_distance(key_vector.reshape((size, 1)), cand_vector.reshape((size, 1)))
                    candidate.append({"response": resp, "score": score, "sentiment": sentiment})
                    visit.append(resp)
        if len(candidate) > n:
            candidate = sorted(candidate, key=lambda item: item["score"], reverse=True)[:n]
        return candidate

    def _read_pair_data_sence(self, keyword: list, st: State, n=10):
        """
        数据库中匹配query和response的关键词，共20条记录
        :param query:
        :param st:
        :param n:
        :return:
        """
        # 过滤一下keyword 太短的
        keyword_ = [word for word in keyword if len(word) > 1]
        if len(keyword_) == 0:
            keyword = ["".join(keyword)]
        else:
            keyword = keyword_
        candidate_lv2 = []  # key- value query response sentiment
        IDS = set()
        condition_sql = "or".join([" {}=\"{}\" ".format("KEYWORD", key) for key in keyword])
        sql = "select KEYWORD,ID_LIST from post_response_index where {}".format(condition_sql)
        self.logger.info("[SQL] execute sql {}".format(sql))
        result = self.database.execute(sql)
        for row in result:
            ids = row[1].split(",")
            for id in ids:
                IDS.add(id)
        # TODO 想办法利用全部ID
        # 受系统限制,受响应速度限制
        if len(IDS) == 0:
            return []
        if len(IDS) > 200:
            IDS = random.sample(IDS, k=200)
        condition_sql = "or".join([" ID={} ".format(id) for id in IDS])
        sql = "select QUERY,RESPONSE,SENTIMENT from post_response_pair where {}".format(condition_sql)
        self.logger.info("[SQL] execute sql {}".format(sql))
        result = self.database.execute(sql)
        for row in result:
            candidate_lv2.append({"query": row[0], "response": row[1], "sentiment": int(row[2])})
        # query和keyword匹配
        key_vector = self._get_sentence_vector(keyword)
        size = key_vector.shape[0]
        can_query = []
        can_response = []
        for can in candidate_lv2:
            db_query_keyword = [word for word, _ in self.text_tool.pos_lcut(can["query"]) if
                                word not in self.dictionary.stop_word]
            db_response_keyword = [word for word, _ in self.text_tool.pos_lcut(can["response"]) if
                                   word not in self.dictionary.stop_word]
            if len(db_query_keyword) > 0:
                db_query_vector = self._get_sentence_vector(db_query_keyword)
                # query
                score = util.cos_distance(key_vector.reshape((size, 1)), db_query_vector.reshape((size, 1)))
                can_query.append(
                    {"query": can["query"], "response": can["response"], "score": score,
                     "sentiment": can["sentiment"]})

            db_response_vector = self._get_sentence_vector(db_response_keyword)
            if len(db_response_keyword) > 0:
                # response
                score = util.cos_distance(key_vector.reshape((size, 1)), db_response_vector.reshape((size, 1)))
                can_response.append(
                    {"query": can["query"], "response": can["response"], "score": score,
                     "sentiment": can["sentiment"]})
        if len(can_query) > n:
            can_query = sorted(can_query, key=lambda x: x["score"], reverse=True)[:n]
        if len(can_response) > n:
            can_response = sorted(can_response, key=lambda x: x["score"], reverse=True)[:n]
        return can_query + can_response


    def _scene(self, query, keyword: list, st: State) -> str:
        """
        在这个内部函数上同一以keyword处理，
        传query是用于生成式的或者检索时回答不得与query相同
        :param query:
        :param keyword:
        :param st:
        :return:
        """

        ai_sentiment = st.get_ai_sentiment()
        candidate_ans = []
        candidate_lv2 = []  # 所有都进lv2进行后续处理
        # TODO 基于文本的，生成模型的，leaning2ask
        pair_data = self._read_pair_data_sence(keyword, st)
        candidate_lv2.extend(pair_data)
        say_data = self._read_user_say_data_sence(keyword, st)
        candidate_lv2.extend(say_data)
        # print(say_data)
        ### 情绪和AI说过的话过滤
        ai_ever_say = st.get_AI_ever_say()
        candidate_lv3 = []
        for item in candidate_lv2:
            response = item["response"]
            if response in ai_ever_say or response == query:
                continue
            sentiment = item["sentiment"]
            if sentiment == _Sentiment.Negative and ai_sentiment == _Sentiment.Negative:
                candidate_lv3.append(response)
            if sentiment != _Sentiment.Negative and ai_sentiment != _Sentiment.Negative:
                candidate_lv3.append(response)
        self.logger.info("candidate lv2-lv3:{}".format(candidate_lv3))
        # 语义进行一次过滤
        candidate_lv4 = []
        for response in candidate_lv3:
            # print("query:",query,"  response:",response)
            score = self._match_score(query, response)
            if score >= config.MATCH_THRESHOLD:
                candidate_lv4.append(response)

        # 排序，按排位赋予被挑选的概率
        candidate_lv4 = self._check_ai_profile(candidate_lv4, st.user_id)
        candidate_lv4 = self._rerank_topic(keyword, candidate_lv4)
        candidate_lv4 = sorted(candidate_lv4, key=lambda x: x["weight"], reverse=True)
        self.logger.info("candidate lv3-lv4:{}".format(candidate_lv4))
        # candidate_lv4每一个item是一个dict
        temp = [{"response": item["response"], "weight": self.get_score_by_rank(i, len(candidate_lv4))} for i, item in
                enumerate(candidate_lv4)]
        candidate_ans.extend(
            self._dropout(temp)
        )
        if len(candidate_ans) == 0:
            candidate_ans.extend(self.default_candidate + ["怎么了？", "什么事呀？"])
        ans = random.choice(candidate_ans)
        return ans

    def get_response(self, query, st: State, keyword=None, keyword_priorty=False):
        """
        用于生成/检索的对话的依据有两种，第一种是query，第二种是query+keyword（or 关系）
        当keyword_priorty为true时，先单纯用keyword，返回空再搜query
        :param query:
        :param st:
        :param keyword:
        :param keyword_priorty:
        :return:
        """
        user_record = st.get_last_User_record()  # USER 当前的实体
        user_entity = user_record.entity
        seg = user_record.segment
        query_keyword = [word for word, _ in seg if word not in self.dictionary.stop_word]
        if keyword or len(user_entity) > 0:
            if keyword is None:
                self.logger.info("[Scene] Scene No keyword")
                ans = self._scene(query, query_keyword, st)
            else:
                # 携带其他keyword
                if not keyword_priorty:
                    # 不优先，一起查
                    self.logger.info("[Scene] Scene keyword no priorty")
                    ans = self._scene(query, query_keyword + keyword, st)
                else:
                    self.logger.info("[Scene] Scene keyword priorty")
                    ans = self._scene(query, keyword, st)
                    if len(ans) == 0:
                        ans = self._scene(query, query_keyword, st)
        else:
            self.logger.info("[Scene] No Scene")
            ans = self._no_scene(query, st)
        # TODO 对答案可能需要做一下改写，保持一致性啥的
        return ans
