# 扫描该目录下的所有文件，找敏感字眼

import os

file = []

self_name = "./scan.py"


def scan_file(file_list):
    for fp in file_list:
        if os.path.isfile(fp) and \
                        "pyc" not in fp and \
                        self_name != fp and \
                        ".idea" not in fp:
            file.append(fp)
        if os.path.isdir(fp):
            scan_file([x.path for x in os.scandir(fp)])


def check_ban_word(line):
    words = ["fuck", "api", "操","Error"]
    for word in words:
        if word in line:
            return True
    return False


scan_file([x.path for x in os.scandir(".")])
error_fp = []
for fp in file:
    try:
        for i, line in enumerate(open(fp, "r", encoding="utf-8")):
            if check_ban_word(line):
                print("{fp} line:{i} :{sen}".format(fp=fp, i=i+1, sen=line))
    except Exception as e:
        error_fp.append("{} has error.e:{}".format(fp, e))

print("########################################################################")
for err in error_fp:
    print(err)
