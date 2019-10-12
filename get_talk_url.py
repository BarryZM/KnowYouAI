import os
import config
import random
import json


def create_key():
    alpaha = "abcdefghijklmnopqrstuvwxyz"
    Alpaha = alpaha.upper()
    number = "1234567890"
    k = random.randint(5, 11)
    key = random.choices(alpaha + Alpaha + number, k=k)
    return "".join(key)


def letstalk(user_id):
    """
    返回web端聊天界面并设置公开密钥
    :return:
    """
    key = create_key()
    dir_ = "./UserData/{}".format(user_id)
    if not os.path.exists(dir_):
        os.makedirs(dir_)
    path = os.path.join(dir_, "web.json")
    json.dump({"key": key}, open(path, "w", encoding="utf-8"))
    url = "来这里玩呀。{host}/web?user_id={user_id}&key={key}".format(host=config.HOST, user_id=user_id, key=key)
    return url


import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("You need to input your user_id.Just like \'python get_talk_url.py your_user_id\' ")
        exit(-1)
    user_id = sys.argv[1]
    ans = letstalk(user_id)
    print(ans)
