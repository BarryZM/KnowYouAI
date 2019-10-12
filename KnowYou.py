from _global import *
from _global.const import _Speaker
from _global.mission import Mission
from core.preprocess import PreProcess
from core.state import State, Record, Knowledge
import itertools
import config
from _global import regex
import random
import traceback
import os
import time


class KnowYou:
    def __init__(self):
        # query预处理模块
        self.preprocess_query = PreProcess()
        # 情绪模块
        self.sentiment = global_sentiment
        # 全局状态
        self.user_id_table = {}
        for master_id in config.MASTER_ID:
            self.user_id_table[master_id] = State(master_id)
        # self.user_id = config.MASTER_ID[0]
        # 主动回话的callback
        self.callback = None
        global_bot_list.initialization()
        # 复读机
        self.flag_rep = False
        # 后台线程池
        # global_threading_pool.start()

    def set_callback(self, callback):
        self.callback = callback
        global_threading_pool.set_callback(callback)

    def _updata_state(self, query, speaker, user_id):
        """
        更新全局状态
        :param query:
        :return:
        """
        seg = global_text_tool.pos_lcut(query)
        ent = global_entity_tool.extract(query)
        common_knowledge = global_entity_tool.get_relation_ship_by_entity(ent)
        sentence_knowledge = []
        if len(ent) > 1:
            comb = itertools.combinations(ent, r=2)
            for item in comb:
                sentence_knowledge = global_entity_tool.relationship_with_entity(item[0], item[1])
        # print(common_knowledge)
        # print(sentence_knowledge)
        knowledge = Knowledge(common_knowledge, sentence_knowledge)
        # print(bg_knowledge)


        user_sentiment = self.sentiment.get_user_sentiment(query, user_id)
        ai_sentiment = self.sentiment.get_ai_sentiment(query, user_id, user_sentiment)
        # 更新user profile
        global_user_profile.update(seg, ent, user_id)
        self.user_id_table[user_id].set_ai_sentiment(ai_sentiment)
        self.user_id_table[user_id].set_user_sentiment(user_sentiment)
        self.user_id_table[user_id].add_record(speaker=speaker, content=query,
                                               entity=ent, segment=seg, knowledge=knowledge)
        # 更新ai being
        global_ai_being.updata(query, user_id)

    def init_userid(self, user_id):
        # self.user_id = user_id
        if user_id not in self.user_id_table:
            self.user_id_table[user_id] = State(user_id)

    def _is_repeater(self, query, st: State):
        user_says = []
        frq = {}
        for item in st.get_dialogue_window():
            if isinstance(item, Record):
                if item.speaker == _Speaker.USER:
                    user_says.append(item.content)
                    frq[item.content] = frq.get(item.content, 0) + 1
        if len(frq) > 0:
            max_frq_sentence = max(frq, key=lambda x: frq[x])
            p = user_says.count(max_frq_sentence) / len(user_says)
            return p >= 0.5 and query == max_frq_sentence and len(st._dialogue_window) > int(
                0.5 * config.WINDOW_SIZE)
        else:
            return False

    def _image_bot_exec(self, image, user_id):
        bot = global_bot_list.match_image_bot(query=image, st=self.user_id_table[user_id])
        if bot:
            response = bot.get_response(image, self.user_id_table[user_id])
        else:
            response = None
        return response

    def _bot_exec(self, query, user_id):
        if self._is_repeater(query, self.user_id_table[user_id]):
            if self.flag_rep:
                response = "不理你噢。(づ ●─● )づ"
            else:
                self.flag_rep = True
                ans = ["你是复读机吗？不理你了。",
                       "人类本质就是复读机。不理你了",
                       "又问一次？再来不理你了",
                       ]
                response = random.choice(ans)
            return response
        self.flag_rep = False
        if regex.help1.search(query) or regex.help2.search(query):
            response = global_bot_list.get_help()
        else:
            bot = global_bot_list.match(query=query, st=self.user_id_table[user_id])
            response = bot.get_response(query, self.user_id_table[user_id])
        return response

    def text_api(self, query, user_id):
        try:
            new_query = self.preprocess_query.preprocess(query, self.user_id_table[user_id])
            if new_query != query:
                global_logger.info("query preprocess: {} -> {}".format(query, new_query))
            self._updata_state(new_query, _Speaker.USER, user_id)
            # 记录对话
            global_session_log.record(self.user_id_table[user_id])
            response = self._bot_exec(new_query, user_id)
            self._updata_state(response, _Speaker.AI, user_id)
            global_logger.info("query:{} response:{}".format(query, response))
            # 主动信息搭话，但暂时不考虑解析用户因此返回的回答,所以搭话以提醒，卖萌为主，而不是询问
            activate_message = global_bot_list.get_bot_remind(new_query, self.user_id_table[user_id])
            if len(activate_message) > 0 and self.callback:
                # 进线程池，不要阻塞主进程回复
                # print("?")
                def func():
                    self.callback(activate_message)
                    if not activate_message.startswith("#"):
                        self._updata_state(activate_message, _Speaker.AI, user_id)
                        # 非特殊回复，记录一下


                mission = Mission("activate", func=func)
                global_threading_pool.add_mission(mission)
        except:
            response = "恭喜你发现了一个bug"
            global_logger.info("Have exception:{}".format(traceback.format_exc()))
        return response

    def img_api(self, img, user_id) -> str:
        """

        :param img:
        :return:
        """
        # TODO 基本逻辑可以这样1.先检索是否有图片技能在text的交互中被激活，有则执行，
        # TODO 整体也是小bot变大bot的原理
        # TODO 默认bot是根据图片转文字，然后调用text_api
        response = self._image_bot_exec(image=img, user_id=user_id)
        if response:
            return response
        else:
            t = int(time.time())
            dir_ = "./UserData/{}/image".format(user_id)
            if not os.path.exists(dir_):
                os.makedirs(dir_)
            path = os.path.join(dir_, "{}.png".format(t))
            img.save(path)
            response = "虽然我知道这个是图片，但暂时处理不了,先保存了"
        self._updata_state(response, _Speaker.AI, user_id)
        global_logger.info("query:{} response:{}".format("#Image", response))
        return response
