import yaml
import os
import json
from PIL import Image
import glob
import config as run_config


def render_params(text: str, user_id, host, robot_ico, robot_ico16, robot_ico48, robot_ico128):
    # <build_params>host</build_params>
    # <build_params>robot_ico</build_params>
    # <build_params>userid</build_params>
    # <build_params>robot_ico16</build_params>",
    # <build_params>robot_ico48</build_params>",
    # <build_params>robot_ico128</build_params>"
    return text.replace("<build_params>host</build_params>", host). \
        replace("<build_params>robot_ico</build_params>", robot_ico). \
        replace("<build_params>userid</build_params>", user_id). \
        replace("<build_params>robot_ico16</build_params>", robot_ico16). \
        replace("<build_params>robot_ico48</build_params>", robot_ico48). \
        replace("<build_params>robot_ico128</build_params>", robot_ico128)


config = yaml.load(open("./build_conf/build.yaml", "r", encoding="utf-8"))
config["agent_profile"]["relationship"] = 10  # 好感度，100分制度
user_id = config["user_id"]

# AI being 储存在该ID名下
path = "./UserData/{}".format(user_id)
if not os.path.exists(path):
    os.makedirs(path)

ai_being_file = os.path.join(path, "ai_being.json")
json.dump(config["ai_being"], open(ai_being_file, "w", encoding="utf-8"))
print("AI being init build.")

# 开辟learn的文件夹
dir_ = os.path.join(run_config.LEARN_PATH, user_id)
if not os.path.exists(dir_):
    os.makedirs(dir_)
    print("Build ", dir_)

# build chrom plugin
chrome_parms = config["chrome_plugin"]
ico_path = chrome_parms["image_ico"]  # ico 路径
host = chrome_parms["host"]
if ico_path == "default":
    ico_path = "./build_conf/chrome_extension/img/robot.png"

# <build_params>host</build_params>
# <build_params>robot_ico</build_params>
# <build_params>userid</build_params>
# <build_params>robot_ico16</build_params>",
# <build_params>robot_ico48</build_params>",
# <build_params>robot_ico128</build_params>"

print("Build chrome extension.....")
DIR = "./UserData/{}/chrome_extension".format(user_id)
# 模板的dir
T_DIR = "./build_conf/chrome_extension"
# 先对图片进行处理
img_dir = os.path.join(DIR, "img")
for d in [DIR, os.path.join(DIR, "img"), os.path.join(DIR, "js")]:
    if not os.path.exists(d):
        os.makedirs(d)
Image.open(os.path.join(T_DIR, "img", "person.png")).save(os.path.join(DIR, "img", "person.png"))
print("Copy person.png")

ico_image = Image.open(ico_path).resize((256, 256))
robot_ico = os.path.join(DIR, "img", "robot_ico.png")
ico_image.save(robot_ico)
print("Build Robot ico.")
# 16
ico_image16 = ico_image.resize((16, 16))
robot_ico16_path = os.path.join(DIR, "img", "robot_ico16.png")
ico_image16.save(robot_ico16_path)
print("Build Robot16 ico.")
# 48
ico_image48 = ico_image.resize((48, 48))
robot_ico48_path = os.path.join(DIR, "img", "robot_ico48.png")
ico_image48.save(robot_ico48_path)
print("Build Robot48 ico.")

# 128
ico_image128 = ico_image.resize((128, 128))
robot_ico128_path = os.path.join(DIR, "img", "robot_ico128.png")
ico_image128.save(robot_ico128_path)
print("Build Robot128 ico.")

# 对文件进行处理
js_file = glob.glob(os.path.join(T_DIR, "js", "*.js"))
for fp in js_file:
    new_path = fp.replace(T_DIR, DIR)
    text = open(fp, "r", encoding="utf-8").read()
    text = render_params(text, user_id, host, robot_ico, robot_ico16_path, robot_ico48_path, robot_ico128_path)
    open(new_path, "w", encoding="utf-8").write(text)
print("Write JS file")

for fp in [os.path.join(T_DIR, "background.html"), os.path.join(T_DIR, "manifest.json"),
           os.path.join(T_DIR, "popup.html")]:
    new_path = fp.replace(T_DIR, DIR)
    text = open(fp, "r", encoding="utf-8").read()
    text = render_params(text, user_id, host, robot_ico, robot_ico16_path, robot_ico48_path, robot_ico128_path)
    open(new_path, "w", encoding="utf-8").write(text)
print("Write Other file")
print("Finish.")


