from .botlist import BotList
from .logging import global_logger
from .dictionary import Dictionary
from util import text_tool, knowledge_graph, entity_tool, pronoun_tool, sentiment, infer, ask
from util import face as face_tool
from core.bots import *
from core.img_bot import *
from core.ai_being import AIBeing
from core.user_profile import UserProfile
from core.threading_pool import ThreadPool
from core.session_log import SessionLog
from core.evalution import Evaluation

#
#  一些工具也变成全局的
#
global_text_tool = text_tool.TextTool()
global_ask_tool = ask.Ask()
global_KG = knowledge_graph.GlobalKG()
global_entity_tool = entity_tool.EntityTool(global_KG, global_text_tool)
global_infer_tool = infer.Infer(global_KG)
global_pronoun_tool = pronoun_tool.PronounTool()
global_threading_pool = ThreadPool()
global_dictionary = Dictionary()
global_ai_being = AIBeing(global_dictionary)
global_user_profile = UserProfile()
global_sentiment = sentiment.Sentiment(
    global_dictionary,
    user_profile=global_user_profile,
    ai_being=global_ai_being
)
global_face_detect = face_tool.FaceIndentify()
EntityObj = entity_tool.EntityObj
global_session_log = SessionLog()
global_eval = Evaluation()

_bot_list = [
    WeiBo(global_text_tool),
    QA(global_infer_tool),
    ShowSentiment(global_ai_being),
    System(global_threading_pool, global_eval),
    StreamDownLoad(global_threading_pool),
    YouGetBiliBili(global_threading_pool),
    New(),
    TeachMe(global_user_profile, global_ai_being),
    Emoji(global_dictionary),
    TaoLu(global_dictionary, global_ai_being)
    # InfoBot(
    #     logger=global_logger,
    #     text_tool=global_text_tool,
    #     dictionary=global_dictionary
    # )
]

global_default_chat = Chat(global_dictionary,
                           global_ai_being,
                           global_user_profile,
                           global_logger,
                           global_ask_tool,
                           global_text_tool)
# _bot_list.append()
global_bot_list = BotList(
    bots=_bot_list,
    image_bot=[Face(global_dictionary, global_face_detect)],
    default_chat_bot=global_default_chat)
