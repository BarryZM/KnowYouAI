from flask import Flask, request, render_template
import json
from learning import Learn
from _global.const import _ResponseType
from flask import render_template
from _global import global_user_profile, global_threading_pool
from UI import *
from KnowYou import KnowYou
import config

from datetime import timedelta

app = Flask(__name__)
# 设置静态文件缓存过期时间
app.send_file_max_age_default = timedelta(seconds=5)

learn = Learn(global_threading_pool)
learn.start()
robot = KnowYou()
weixin_robot = WeiXin(robot)
browser = Browser(robot)
web = Web(robot)


@app.route("/extension", methods=["POST", "GET"])
def activate_learning():
    """
    接受插件在网页内抽取的多项p文本
    :return:
    """

    json_obj = request.get_json(force=True)
    result = {}
    url = json_obj["url"]
    if  config.HOST not in url:
        """
        本地的页面不学
        """
        print("Get the page..")
        ps = json_obj["p"]
        print("Len:", len(ps))
        user_id = json_obj.get("user_id", "DEFAULT")
        learn.learn(url, ps, user_id=user_id)
    # 回复一下浏览器，否则会不断问
    result["type"] = _ResponseType.Nothing
    result["response"] = "OK"
    return json.dumps(result)


@app.route("/teach")
def teach():
    params = request.args
    user_id = params.get("user_id")
    key = params.get("key")
    off_key = global_user_profile.get("key", user_id)
    if key != off_key:
        return "forbidden"
    without_att = global_user_profile.entity_no_attitude(user_id)
    # 载入user profile
    words = [(i + 1, ent) for i, ent in enumerate(without_att)]  # [(1, "FFF"), (2, "AAAA")]
    return render_template("teach_index.html", words=words, size=len(words), user_id=user_id, host=config.HOST)


@app.route("/submit", methods=["POST"])
def submit():
    """
    提交标注结果
    :return:
    """
    json_obj = request.get_json(force=True)
    user_id = json_obj["user_id"]
    attitude = json.loads(json_obj["attitude"])
    global_user_profile.update_attitude(user_id, attitude)
    return json.dumps({"status": "success"})


@app.route("/extension_dialogue", methods=['POST', 'GET'])
def extension_dialogue():
    """
    插件聊天
    目前只支持text类型的回复和请求
    :return:
    """
    json_obj = request.get_json(force=True)
    query = json_obj["query"]
    user_id = json_obj.get("user_id", "DEFAULT")
    response = browser.get_response(query, user_id)
    result = {"response": response}
    return json.dumps(result)


@app.route("/weixin", methods=['POST', 'GET'])
def weixin():
    if request.method == "GET":
        echostr = request.args['echostr']
        return echostr
    xml = request.stream.read()  # 阅读512个字符
    msg = parse_message(xml)
    result = weixin_robot.get_response(msg)
    return result


@app.route("/web", methods=['POST', 'GET'])
def web_deal():
    if request.method == "GET":
        # 返回主页
        # 验证
        user_id = request.args.get("user_id")
        key = request.args.get("key")
        if not all([key, user_id]):
            return "Forbidden", 500
        dir_ = "./UserData/{}".format(user_id)
        path = os.path.join(dir_, "web.json")
        if not os.path.exists(dir_):
            os.makedirs(dir_)
            json.dump({"key": key}, open(path, "w", encoding="utf-8"))
        parse_json = json.load(open(path, "r", encoding="utf-8"))
        off_key = parse_json["key"]
        if key == off_key:
            return render_template("web_bot.html", user_id=user_id, host=config.HOST)
        else:
            return "Forbidden", 500
    else:
        # POST 返回数据
        json_obj = request.get_json(force=True)
        query = json_obj["query"]
        user_id = json_obj.get("user_id", "DEFAULT")
        response = web.get_response(query, user_id)
        time.sleep(0.3)  # 等一下主动搭话的线程同步
        activate_say = web.active_say[user_id]
        result = {
            "response": response,
            "activate": activate_say if activate_say else ""
        }
        return json.dumps(result)


ALLOWED_EXTENSIONS = ['png', 'jpg', 'JPG', 'PNG', 'bmp', 'jpeg']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/web_image", methods=['POST', 'GET'])
def web_image():
    user_id = request.args.get("user_id", "DEFAULT")
    f = request.files['file']
    if not (f and allowed_file(f.filename)):
        return json.dumps({"error": 1001, "msg": "请检查上传的图片类型，仅限于png、PNG、jpg、JPG、bmp"})
    temp_path = "./UserData/{}/image/{}".format(user_id, f.filename)
    f.save(temp_path)
    img = PIL_Image.open(temp_path)
    response = web.get_img_response(img, user_id)
    time.sleep(0.3)  # 等一下主动搭话的线程同步
    activate_say = web.active_say[user_id]
    result = {
        "response": response,
        "activate": activate_say if activate_say else ""
    }
    # result["activate"] = activate_say
    return json.dumps(result)


@app.route("/test", methods=['POST', 'GET'])
def test():
    return "OK"


if __name__ == "__main__":
    # open("")
    app.run(host="0.0.0.0", port=80, debug=True, use_reloader=True)
    # app.run(host="0.0.0.0", port=80, debug=True)
