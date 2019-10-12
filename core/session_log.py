from core.state import State
import time
import json
import os


class SessionLog:
    """
    对话记录
    写入文件，每一行都是一个json
    """

    def __init__(self):
        # self.buffer = [] # 满足1000就换文件
        self.path = "./UserData/{user_id}/say.txt"
        self.time = time.time()
        self.user_id_file = {}

    def record(self, st: State):
        user_id = st.user_id
        path = self.path.format(user_id=user_id)
        if user_id not in self.user_id_file:
            if os.path.exists(path):
                self.user_id_file[user_id] = open(path, "a", encoding="utf-8")
            else:
                self.user_id_file[user_id] = open(path, "w", encoding="utf-8")
        file = self.user_id_file[user_id]
        ai_record = st.get_last_AI_record()
        user_record = st.get_last_User_record()
        data = {
            "query": "" if ai_record is None else ai_record.content,  # AI说的上一句
            "query_entity": [] if ai_record is None else [item.to_dict() for item in ai_record.entity],
            "response_sentiment": st.get_user_sentiment(),  # user当前的情绪
            "response": user_record.content,
            "response_entity": [item.to_dict() for item in user_record.entity],
        }
        string = json.dumps(data)
        file.write(string + "\n")
        file.flush()
