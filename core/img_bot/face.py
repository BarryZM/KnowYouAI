from core.bots._base import Bot
from core.state import State
from _global import regex
from _global.const import _Score
import random
from PIL import Image
import time


class Face(Bot):
    """
    通过人脸检测技术，获取人脸相关信息
    然后做进一步的选择
    """
    Wait = 1

    def __init__(self, dictionary, face_tool):
        super(Face, self).__init__()
        self.dictionary = dictionary
        self.face_tool = face_tool

    def activate_match(self, query, st: State):
        return "小姐姐" in query or "小哥哥" in query

    def activate_say(self, query, st):
        return "你可以说\"看脸术\"来让我看看小姐姐小哥哥的颜值噢"

    def match(self, query, st: State):
        """
        image bot比较特殊，query可能是str也可能是image
        :param query:
        :param st:
        :return:
        """
        user_id = st.user_id
        if user_id not in self.user_id_table:
            self.user_id_table[user_id] = Face.Init
        if isinstance(query, str):
            flag = regex.see_face.search(query)
        else:
            flag = (self.user_id_table[user_id] != Face.Init)
        s = _Score.LevelNormal if flag else 0
        return flag, s

    def get_response(self, query, st: State):
        user_id = st.user_id
        if self.user_id_table[user_id] == Face.Init:
            self.user_id_table[user_id] = Face.Wait
            return random.choice([
                "OK,你可以把图片发过来了",
                "把图片发过来看看"
            ])
        else:
            # 匹配成功时，不可能是字符进来
            t = int(time.time())
            if isinstance(query, Image.Image):
                path = "./UserData/tmp/{}.png".format(t)
                query.save(path)
                result = self.face_tool.detect_face(path)
                gender = result["gender"]
                age = result["age"]
                ans = "{},看起来{}岁了"
                if gender == "female":
                    ans = ans.format("小姐姐", age)
                else:
                    ans = ans.format("小哥哥", age)
                self.user_id_table[user_id] = Face.Init
                return ans

            else:
                return "你是魔鬼吗，怎么进来了？"
