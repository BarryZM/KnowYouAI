import threading
import requests
import config
from wechatpy.client import WeChatClient


class Weixin:
    def __init__(self):
        self.token = ""
        self.get_token()

        self.appid = config.APP_ID
        self.appsecret = config.APPSECRET
        self.client = WeChatClient(self.appid, self.appsecret)
        threading.Timer(6000, self.get_token())

    def get_token(self):
        self.appid = config.APP_ID
        self.appsecret = config.APPSECRET
        get_token_url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}". \
            format(self.appid, self.appsecret)
        result = requests.get(get_token_url)
        json_obj = result.json()
        if "access_token" in json_obj:
            self.token = json_obj["access_token"]
            # logger.global_logger.debug("get the token:{}".format(self.token))
        else:
            err = json_obj["errmsg"]
            # logger.global_logger.debug("can't not get the token:{}".format(err))

    def upload(self, image_path):
        type_ = "image"
        url = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=%s" % (self.token, type_)
        files = {'media': open('{}'.format(image_path), 'rb')}
        r = requests.post(url, files=files)
        json_obj = r.json()
        return json_obj.get("media_id")

    def send_text(self, user_id, content):

        self.client.message.send_text(user_id, content)
        # client.message.send_text('user id', 'content')

    def send_image(self, user_id, media_id):
        self.client.message.send_image(user_id, media_id)
