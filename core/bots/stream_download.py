from core.bots._base import Bot
from core.state import State
from _global import regex
from _global.const import _Score
from _global.mission import Mission
from util import download_tool
import os
import time


class StreamDownLoad(Bot):
    def __init__(self, pool):
        super(StreamDownLoad, self).__init__()
        self.pool = pool
        self.image_format = ["jpg", "jpeg", "gif", "png"]
        self.video_format = ["mp4", "avi"]
        self.audio_format = ["wav", "mp3"]
        self.format = None

        self.finish = False  # 用于完成了主动搭话

    def match(self, query, st):
        self.format = None
        formats = self.image_format + self.video_format + self.audio_format
        for format_ in formats:
            if query.endswith(format_):
                self.format = format_
                return True, _Score.LevelNormal
            if format_ + "?" in query:
                self.format = format_
                return True, _Score.LevelNormal
            if format_ + "&" in query:
                self.format = format_
                return True, _Score.LevelNormal
        return False, 0

    def helper(self):
        return ["给我一个mp4/jpg之类的链接我能直接下载噢"]

    def activate_match(self, query, st: State):
        return self.finish

    def activate_say(self, query, st):
        self.finish = False
        return "下载任务完成啦"

    def get_response(self, query, st: State):
        user_id = st.user_id
        formats = self.image_format + self.video_format + self.audio_format
        for format_ in formats:
            if query.endswith(format_):
                self.format = format_
            if format_ + "?" in query:
                self.format = format_
        # 直接query就是url
        url = regex.url.search(query)[0]
        if self.format in self.image_format:
            tag = "img"
        elif self.format in self.video_format:
            tag = "video"
        else:
            tag = "audio"
        dir_ = os.path.join("./UserData/{}".format(user_id), tag)
        if not os.path.exists(dir_):
            os.makedirs(dir_)
        path = os.path.join(dir_, "{}.{}".format(int(time.time()), self.format))

        def func():
            try:
                download_tool.stream_download(url, path, timeout=10)
                self.finish = True
            except Exception as e:
                """
                留给线程池处理
                """
                raise e

        # t = Thread(target=func)
        # t.setDaemon(True)
        # t.start()
        mission = Mission(name="download: {}".format(url), func=func)
        self.pool.add_mission(mission)
        return True, "我开始下载{}了咯".format(url)
