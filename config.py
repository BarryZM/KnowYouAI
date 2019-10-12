LOGGING = "./log/ai_log_{}.txt"
WINDOW_SIZE = 25  # 对话窗口的大小，也是检索上下文信息时的最大感受野。
JIEBA_DICT_PATH = "./assets/jieba_dict"

MASTER_ID = ["MASTER"]  # Default user id
WEIXIN_ID2USER_ID = {
}
THRESHOLD_BOT = 0.1  # BOT的匹配阈值
MAX_HELP = 6  # 查找帮助时最大的帮助信息
HOST = "http://localhost"  # 有时要给出链接，让用户参与传统的交互方式，如人工标注。这时地址的主机
MATCH_THRESHOLD = 0.7  # default chat中的语义匹配阈值
MATCH_CANDIDATE = 10  # 候选答案个数
WEIXIN_STYLE = True  # 微信一样的对话框，支持图片，文字表情等

NEO4F_CONF = {
    "url": "http://localhost:7474",
    "username": "neo4j",
    "password": "rabbit"
}
### path
LEARN_PATH = "./UserData/learn"
PRAISE_PATH = "./assets/praise.txt"
CURSE_PATH = "./assets/curse.txt"
QAQ_PATH = "./assets/QAQ"
BAN_PATH = "./assets/ban_word.txt"
PAIR_DIR = "./assets/pair"
MATCH_W2I_PATH = "./assets/nn/w2i.json"  # MATCH 网络的词库
MATCH_CHECKPOINT = "./assets/checkpoints"  # MATCH 网络的权重
CQA_PATH = "./assets/cqa/cQA.db"  # 社区问答的数据，给与info bot但并不是做QA
EMOJI_PATH = "./assets/emoji"
STOP_WORD = "./assets/stop_word.txt"
END_WORD = "./assets/end_word.txt"
AFFIME_PATH = "./assets/affirm"
ENTITY_PATH = "./assets/entity"
WORD2VECTOR_PATH = "./assets/checkpoints/word2vec_wordlevel_20190730_kv"
POST_RESPONSE_PATH = "./assets/post_response/post_response.db"
TF_IDF_PATH = "./assets/post_response/tf_idf.json"
###


INFO_ACKNOWLEDGE = True  # 后台进程有消息时缓存还是读取
THREADING_POOL_SIZE = 5  # 后台任务大小

AI_BEING_UPDATE_ITER = 10  # 每5轮保存一次
USER_PROFILE_UPDATE_ITER = 10  # 每5轮保存一次

##
BAIDU_TOKEN = "24.a3866551bfc2eb3b873f29e8ebbef8ce.2592000.1572425204.282335-16639333"
