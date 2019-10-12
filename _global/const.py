class _MessageType:
    Normal = 100
    URL = 101
    FILE = 102
    Image = 200
    Struct = 300  # 既含图像又含文本等，全部解释成结构化信息
    ALL = 400


class _ResponseType:
    Nothing = "nothing"
    Text = "text"
    Image = "image"
    Dict = "dict"


class _Speaker:
    AI = "AI"
    USER = "USER"


class _Identity:
    Master = 0
    Guest = 1

    def __init__(self):
        self._identity = _Identity.Master

    @property
    def identity(self):
        return self._identity

    @identity.setter
    def identity(self, identity):
        self._identity = identity


global_identity = _Identity()


class _State:
    Unconscious = 0  # 普通的状态
    TaoLu = 1  # 按照AI的问话直接匹配，套路


class _Score:
    LevelTop = 1
    LevelHight = 0.9
    LevelNormal = 0.7
    LevelLow = 0.5

class _Topic:
    # 优先级

    # 数据库匹配中要全部大写
    # 知识图谱中是小写
    Personal = "personal"
    Unknown = "unknown"
    People = "people_name"
    City = "city"  # 地理相关
    Time = "time"  # 时间
    Festival = "festival"  # 节假日
    Movie = "movie"
    Music = "music"
    Anime = "anime"
    Health = "health"
    Relationship = "relationship"
    Weather = "weather"
    Play = "play"
    Sport = "sport"
    Animal = "animal"
    Plant = "plant"
    Food = "food"  # 各种，小吃，主菜等
    Mood = "mood"


class _Sentiment:
    Negative = -1
    Normal = 0
    Positive = 1
