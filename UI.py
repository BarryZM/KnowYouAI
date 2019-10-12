from wechatpy import parse_message
import requests
from wechatpy.client.api import WeChatMedia
import random
from _global import regex
from wechatpy.replies import TextReply, ImageReply
from KnowYou import KnowYou
import json
import time
import config
import os
from util import download_tool, weixin_unit
from PIL import Image as PIL_Image


class WeiXin:
    def __init__(self, ai: KnowYou):
        self.ai = ai
        self.weixin_id = None
        # 微信在没回复的时候，回继续发起请求，机器人容易蒙蔽
        # 用个对象记录下
        self.visist = {
            "count": 0,
            "visit_id": 0
        }
        # user_id 映射表，微信号对应身份，如果没有对应的，就以该id为准
        self._weixin_id2user_id = config.WEIXIN_ID2USER_ID
        self._weixin_util = weixin_unit.Weixin()

    def _create_key(self):
        alpaha = "abcdefghijklmnopqrstuvwxyz"
        Alpaha = alpaha.upper()
        number = "1234567890"
        k = random.randint(5, 11)
        key = random.choices(alpaha + Alpaha + number, k=k)
        return "".join(key)

    def letstalk(self, user_id):
        """
        返回web端聊天界面并设置公开密钥
        :return:
        """
        key = self._create_key()
        dir_ = "./UserData/{}".format(user_id)
        if not os.path.exists(dir_):
            os.makedirs(dir_)
        path = os.path.join(dir_, "web.json")
        json.dump({"key": key}, open(path, "w", encoding="utf-8"))
        url = "来这里玩呀。{host}/web?user_id={user_id}&key={key}".format(host=config.HOST, user_id=user_id, key=key)
        return url

    def callback(self, message: str):
        # 框架主动执行的，不需要返回一个xml
        # 图片型
        if self.weixin_id is None:
            return
        if message.startswith("#Image"):
            path = message.replace("#Image:", "")
            medie_id = self._weixin_util.upload(path)
            self._weixin_util.send_image(self.weixin_id, medie_id)
        else:
            # 文本型的xml
            if message.startswith("#json:"):
                message = message.replace("#json:", "")
                response_json = json.loads(message)
                # print(response_json)
                # 处理url类的
                for key in response_json:
                    if "url" in key:
                        message = "你自己看吧。\n{}".format(response_json[key])
                        break
            self._weixin_util.send_text(user_id=self.weixin_id, content=message)

    def _response2xml(self, response, msg):
        """
        将response解析成需要的xml
        :param response:
        :return:
        """
        # 图片型
        if response.startswith("#Image"):
            path = response.replace("#Image:", "")
            medie_id = self._weixin_util.upload(path)
            replay = ImageReply(media_id=medie_id, message=msg)
            xml = replay.render()
            return xml
        else:
            # 文本型的xml
            if response.startswith("#json:"):
                response = response.replace("#json:", "")
                response_json = json.loads(response)
                # print(response_json)
                # 处理url类的
                for key in response_json:
                    if "url" in key:
                        response = "你自己看吧。\n{}".format(response_json[key])
                        break
            reply = TextReply(content=response, message=msg)
            xml = reply.render()
            return xml

    def get_response(self, msg):
        """
        测试是否微信服务器的重复请求,再根据类型响应
        :param msg:
        :return:
        """
        if msg.id == self.visist["visit_id"]:
            self.visist["count"] += 1
            print("weixin request again.")
            if self.visist["count"] > 2:
                ans = "脑壳疼,缓一缓"
                reply = TextReply(content=ans, message=msg)
                xml = reply.render()
                # AI.initialization()  # 重启
                return xml
            time.sleep(5)  # 拖时间，确认不会影响到还在执行的回复
            return ""
        else:
            # self.ai.set_callback(self.callback)
            self.visist["visit_id"] = msg.id
            self.visist["count"] = 0
            self.weixin_id = msg.source
            user_id = self._weixin_id2user_id.get(self.weixin_id, self.weixin_id)
            self.ai.init_userid(user_id)
            # print()
            if msg.type == 'text':
                query = msg.content
                if query == "来聊天":
                    response = self.letstalk(user_id)

                else:
                    response = self.ai.text_api(query,user_id)
                xml = self._response2xml(response, msg)
                return xml
            elif msg.type == "image":
                url = msg.image
                # 先下载，再读取
                path = "./UserData/tmp/"
                if not os.path.exists(path):
                    os.makedirs(path)
                name = "{}.png".format(msg.source)  # 以用户id做名字，避免乱串
                path = os.path.join(path, name)
                download_tool.stream_download(url, path)
                image = PIL_Image.open(path)
                response = self.ai.img_api(image,user_id)
                xml = self._response2xml(response, msg)
            else:
                reply = TextReply(content="暂时不支持该数据格式", message=msg)
                xml = reply.render()
            return xml


class Browser:
    def __init__(self, ai: KnowYou):
        self.ai = ai

    def _post_process(self, response: str):
        """
        处理特殊的文字输出
        :param response:
        :return:
        """
        if response.startswith("#json:"):
            response = response.replace("#json:", "")
            response_json = json.loads(response)
            # print(response_json)
            # 处理url类的
            for key in response_json:
                if "url" in key:
                    response = "你自己看吧。\n{}".format(response_json[key])
                    return response
        if response.startswith("#Image:"):
            # 处理图片类的
            response = "本来想给个图片你的，可是这个端还不支持。"
            # response = "\n".join(["{}:{}".format(key, value) for key, value in response_json.items()])
        return response

    def get_response(self, query, user_id):
        self.ai.set_callback(None)
        self.ai.init_userid(user_id)
        response = self.ai.text_api(query,user_id)
        response = self._post_process(response)
        return response


class Web:
    """
    web端
    """

    def __init__(self, ai: KnowYou):
        self.ai = ai
        self.max_image_size = 180
        self.active_say = {}

    def _reisze_image(self, pil_image: PIL_Image.Image):
        h, w = pil_image.size
        if w > h:
            nw = self.max_image_size
            nh = nw * (h / w)
        else:
            nh = self.max_image_size
            nw = nh * (w / h)
        return pil_image.resize((int(nh), int(nw)))

    def _deal_message(self, message, user_id):
        """
        对message进行后处理
        :param message:
        :return:
        """
        response = message.replace("\n", "<br>")

        if message.startswith("#Image"):
            path = message.replace("#Image:", "")
            base_name = os.path.basename(path)
            dir_ = "./static/tmp"
            if not os.path.exists(dir_):
                os.makedirs(dir_)
            tmp_path = os.path.join(dir_, base_name)
            image = PIL_Image.open(path)
            image = self._reisze_image(image)
            image.save(tmp_path)
            # 计算图片比例整理尺寸
            response = "<img src=\' {} \'/>".format(tmp_path)
        else:
            # 文本型的xml
            if message.startswith("#json:"):
                message = message.replace("#json:", "")
                response_json = json.loads(message)
                # print(response_json)
                # 处理url类的
                for key in response_json:
                    if "url" in key:
                        response = "你自己看吧。\n<a href=\'{href}\'> {href}</a>".format(href=response_json[key])
                        break
            else:
                f = regex.html_tag.search(message)
                if f:
                    response = response.replace(f[0], "<a href=\'{href}\'> {href}</a>".format(href=f[0]))
        return response

    def get_call_back(self, user_id):
        def callback(message):
            message = self._deal_message(message, user_id)
            self.active_say[user_id] = message

        return callback

    def get_response(self, query, user_id):
        self.ai.set_callback(self.get_call_back(user_id))
        self.active_say[user_id] = None
        self.ai.init_userid(user_id)
        response = self.ai.text_api(query,user_id)
        response = self._deal_message(response, user_id)
        return response

    def get_img_response(self, img, user_id):
        self.ai.set_callback(self.get_call_back(user_id))
        self.active_say[user_id] = None
        self.ai.init_userid(user_id)
        response = self.ai.img_api(img, user_id)
        response = self._deal_message(response, user_id)
        return response
