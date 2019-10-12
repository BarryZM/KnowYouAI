import re

weibo_re = re.compile("看(?P<name>[^的|.]{0,})的{0,1}微博")
help1 = re.compile("你.{0,5}(懂|会|能做).{0,}(什么|吗)")
help2 = re.compile("^(你能帮我).{1,}")

# 上下文疑问的
content_pattern1 = re.compile(r"^那.{1,}呢\?{0,1}$")

# 去除html标签
# 记录原文
html_tag = re.compile(r"\</{0,1}.{1,}\>")

system_resource1 = re.compile(r"(查看|查询|告诉我)系统资源(情况){0,1}$")
system_resource2 = re.compile(r"^系统(资源|情况)$")
system_ability = re.compile(r"^(能力评估)|(对话能力)$")

url = re.compile(r"(http|ftp|https):[^\u4e00-\u9fa5]{1,}")
url2 = re.compile(
    r"(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?[^\u4e00-\u9fa5]")
youget_number = re.compile("#\d{1,2}")

alpah_number_sym = re.compile("[^A-Za-z0-9\!\%\[\]\,\。\.\://]")

new_re = re.compile(".{0,10}有什么(?P<type>(头条|社会|国内|娱乐|体育|军事|科技|财经|时尚){0,1})类{0,1}的{0,1}新闻")

# 代词
pro_re = re.compile("(她|他们|她们|我|我们|他)")

# 无监督新话题开头
new_topic_being = re.compile("(今天|最近|昨天|有一次|刚刚|听说|有次|前天)")

# 图像技能：看脸术
see_face = re.compile("^看脸术$")

why = re.compile("^为什么呢{0,1}\?{0,1}$")
why2 = re.compile("^这么.{1,}的吗{0,1}\?{0,1}$")
# 用户的命令的句子，不允许在检索对话时匹配
command = [
    re.compile("^请"),
    re.compile("^我要.{1,}你$"),
    re.compile("^你能"),
    re.compile("^查询"),
    re.compile("^对话能力"),
]