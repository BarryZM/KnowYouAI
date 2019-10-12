from core.bots._base import Bot
from core.state import State
from _global import regex
from _global.const import _Score
from _global.mission import Mission
import os
import time
import subprocess


class YouGetBiliBili(Bot):
    def __init__(self, pool):
        super(YouGetBiliBili, self).__init__()
        self.pool = pool
        self.download_dict = {}  # 表示号对应子进程号 格式两位数字 #dd
        self.download_name_dict = {}  # 表示号对应title 格式两位数字 #dd
        self.url = None
        self.act = False
        self.act_message = ""

    def match(self, query, st):
        self.url = regex.url2.search(query)
        # 目前只考虑BiliBili
        return any([self.url is not None and "bilibili" in self.url[0],
                    "youget" in query,
                    "you_get" in query,
                    "you-get" in query,
                    "YOUGET" in query]), _Score.LevelNormal

    def helper(self):
        return ["给我一个B站视频的链接我能直接下载噢"]

    def activate_match(self, query, st: State):
        return self.act

    def activate_say(self, query, st):
        self.act = False
        return self.act_message

    def get_response(self, query, st: State):
        user_id = st.user_id
        self.url = regex.url2.search(query)
        if "取消" in query or "#" in query:
            if query.startswith("#"):
                # 回答即id
                id = query
            else:
                id = regex.youget_number.search(query)  # 进程标识
                if id is not None:
                    id = id[0]
            if id is None or id not in self.download_dict:
                ans = "没有找到合适的id。\n" if id is None else "没有找到{}。\n".format(id)
                ans += "你需要取消下载哪一个？\n\n"
                for id, title in self.download_name_dict.items():
                    ans += "- [{id}]:{title}\n".format(id=id, title=title)
            else:
                pro = self.download_dict[id]
                pro.terminate()
                del self.download_dict[id]
                del self.download_name_dict[id]
                ans = "已经取消啦"
            return ans
        elif self.url is not None:
            # 先去掉中文等杂音
            url = regex.alpah_number_sym.sub("", self.url[0])
            # 先抽取标题
            # cmd = "you-get {url} --json".format(url=url)
            # p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            # out = p.stdout.read()
            #
            # parsed_json = json.loads(out.decode())
            title = url  # parsed_json["title"]

            def func():
                try:
                    out_stream = open("./UserData/tmp/youget_output.txt", "w")
                    dir_ = os.path.join("./UserData/{}".format(user_id), "video")
                    if not os.path.exists(dir_):
                        os.makedirs(dir_)
                    output_dir = os.path.join(dir_, str(int(time.time())))
                    cmd = "you-get {url} --output-dir {output} -a -l".format(url=url,
                                                                             output=output_dir)
                    id = "#{}".format(len(self.download_dict))
                    self.download_name_dict[id] = title
                    self.download_dict[id] = subprocess.Popen(cmd.split(" "),
                                                              shell=False, stdout=out_stream,
                                                              stderr=subprocess.PIPE)
                    self.download_dict[id].wait()
                    out_stream.close()
                    # 下载完成/错误/主动取消都会跳出wait,检测是否要主动提醒
                    if id in self.download_dict:
                        # 如果主动取消就不会存在dict里了
                        error_info = self.download_dict[id].stderr.read()
                        if len(error_info) == 0:
                            self.act = True
                            self.act_message = "{}下载完成咯。保存在{}".format(title, output_dir)
                        else:
                            self.act = True
                            self.act_message = "下载出问题了。\n问题报告:{}".format(error_info)
                        del self.download_dict[id]
                        del self.download_name_dict[id]
                except Exception as e:
                    raise e

            # t = Thread(target=func)
            # t.setDaemon(True)
            # t.start()
            mission = Mission(name="you-get: {}".format(url), func=func)
            self.pool.add_mission(mission)
            ans = "我在用you-get下载{}了哦。\n视频名字叫：{}".format(url, title)
            self.url = None
            return ans
