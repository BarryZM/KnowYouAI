from _global import regex
import os
import time
import config
import requests
import jieba
from jieba import posseg
import random
import json
from _global.mission import Mission
from queue import Queue


class Learn:
    def __init__(self, threading_pool):
        self._save_dir = os.path.join(config.LEARN_PATH, "{user_id}")
        self.token = jieba.Tokenizer()
        self.pos_token = posseg.POSTokenizer(self.token)
        self.threading_pool = threading_pool
        self.queue = Queue()

    def start(self):
        mission = Mission("learning", func=self._exec)
        self.threading_pool.add_mission(mission)

    def get_mention_concept(self, text):
        headers = {"content-type": "application/json"}
        url = "https://aip.baidubce.com/rpc/2.0/kg/v1/cognitive/entity_annotation?access_token={}".format(
            config.BAIDU_TOKEN)
        data = {"data": text}
        response = requests.post(url, headers=headers, json=data)
        parsed_json = response.json()
        result = []  # (mention concept-level1)
        if "entity_annotation" not in parsed_json:
            # print("text:{} can't not find anything.".format(text))
            # print(parsed_json)
            return result
        for entity in parsed_json["entity_annotation"]:
            mention = entity["mention"]
            concept = entity["concept"]["level1"]
            result.append((mention, concept))
        return result

    def get_mention_concept_sizi(self, text):
        keyword = self.pos_token.lcut(text)
        url = "https://api.ownthink.com/kg/knowledge?entity={}"
        result = []
        for i, (word, tag) in enumerate(keyword):
            if "nr" == tag:
                if len(word) != 1:
                    result.append((word, "人物"))
                else:
                    if (i + 1) != len(keyword):
                        w, _ = keyword[i + 1]
                        result.append(("".join([word, w]), "人物"))
            if "n" in tag:
                if any(["师" in word, "博士" in word, "教授" in word]):
                    result.append((word, "人物"))
                else:
                    new_url = url.format(word)
                    try:
                        respongse = requests.get(new_url, timeout=3)
                        parsed_json = respongse.json()
                        tags = parsed_json["tag"]
                        for tag in tags:
                            result.append((word, tag))
                    except:
                        pass
        return result

    def extract_entity(self, sentence):
        """
        目的是挖掘新的实体，所以调用别人的API
        :return:
        """
        # if random.uniform(0, 1) > 0.5:
        #     men_and_con = self.get_mention_concept_sizi(sentence)
        #     time.sleep(0.1)
        # # 百度接口
        # else:
        #     men_and_con = self.get_mention_concept(sentence)
        if len(sentence) < 5:
            return []
        men_and_con = []
        men_and_con.extend(self.get_mention_concept_sizi(sentence))
        men_and_con.extend(self.get_mention_concept(sentence))
        time.sleep(0.3)
        entitys = []
        topic = set()
        if len(men_and_con) == 0:
            topic.add("unknown")
        else:
            for mention, concept in men_and_con:
                # 不符合以下的实体就不要加了
                con = "unknown"
                pros = "这"
                if "人物" in concept:
                    con = "people_name"
                    pros = "这个人"
                    topic.add(con)
                    line = "{name}|{labels}|{pros}|{topic}".format(
                        name=mention,
                        labels=con,
                        pros=pros,
                        topic=con,
                    )
                    entitys.append(line)
                elif "地理" in concept or "城市" in concept:
                    con = "city"
                    pros = "这里"
                    topic.add(con)
                    line = "{name}|{labels}|{pros}|{topic}".format(
                        name=mention,
                        labels=con,
                        pros=pros,
                        topic=con,
                    )
                    entitys.append(line)
                elif "音乐" in concept:
                    con = "music"
                    pros = "这首歌"
                    topic.add(con)
                    line = "{name}|{labels}|{pros}|{topic}".format(
                        name=mention,
                        labels=con,
                        pros=pros,
                        topic=con,
                    )
                    entitys.append(line)
                elif "医学" in concept:
                    con = "health"
                    topic.add(con)
                    line = "{name}|{labels}|{pros}|{topic}".format(
                        name=mention,
                        labels=con,
                        pros=pros,
                        topic=con,
                    )
                    entitys.append(line)
                elif "食物" in concept:
                    con = "food"
                    topic.add("food")
                    line = "{name}|{labels}|{pros}|{topic}".format(
                        name=mention,
                        labels=con,
                        pros=pros,
                        topic=con,
                    )
                    entitys.append(line)
                elif "情感" in concept:
                    con = "mood"
                    topic.add("mood")
                    line = "{name}|{labels}|{pros}|{topic}".format(
                        name=mention,
                        labels=con,
                        pros=pros,
                        topic=con,
                    )
                    entitys.append(line)
                else:
                    topic.add("unknown")
        return entitys

    def _ps2sentence(self, ps):
        """
        将所有句子按照，。！来切割成一个个句子。
        :param ps:
        :return:
        """
        article = "。".join(ps)
        split_tag = "<split>"
        article = article.replace("。", split_tag) \
            .replace("?", split_tag).replace("？", split_tag).replace("\n", split_tag)
        sentences = article.split(split_tag)
        return sentences

    def extract_new_dialouge_sentence(self, sentences: list):
        """
        抽取可以用作新的一轮对话开头的句子
        :param sentences:list
        :return:
        """
        result = []
        for sen in sentences:
            if regex.new_topic_being.search(sen):
                result.append(sen)
        return result

    def _learn(self, url, ps, user_id):
        """

        :param url:访问的url
        :param ps: P元素的集合（段落的列表）
        :return:
        """
        path = self._save_dir.format(user_id=user_id)
        if not os.path.exists(path):
            os.makedirs(path)
        t = int(time.time())
        # 记录原文
        ps = [regex.html_tag.sub("", p) for p in ps]  # 去除html标签
        sentences = self._ps2sentence(ps)
        new_dialouge_begin = self.extract_new_dialouge_sentence(sentences)
        if len(new_dialouge_begin) > 0:
            open(os.path.join(path, "{}_begin.txt".format(t)), "w", encoding="utf-8") \
                .write("\n".join(["<url>" + url + "</url>"] + new_dialouge_begin))
            print("Write dialogue Begin txt")

        open(os.path.join(path, "{}_p.txt".format(t)), "w", encoding="utf-8") \
            .write("\n".join(["<url>" + url + "</url>"] + ps))
        print("Record all p")
        # 每一个段落
        entity_set = set()
        for sentence in sentences:
            # print("Extract sentence....", sentence)
            entity = self.extract_entity(sentence)
            # print(entity)
            for ent in entity:
                entity_set.add(ent)

        # 记录实体
        if len(entity_set) > 0:
            fp = open(os.path.join(path, "{}_entity.txt".format(t)), "w", encoding="utf-8")
            for entity_line in entity_set:
                fp.write(entity_line + "\n")
            fp.close()
            print("Learn the entity.")
            # 记录实体出现频率，做为另一个学习到的user profile
            path = os.path.join(path, "user_profile.json")
            if not os.path.exists(path):
                empty_data = {
                    "tf": {}
                }
                json.dump(empty_data, open(path, "w", encoding="utf-8"))
            data = json.load(open(path, "r", encoding="utf-8"))
            for entity_line in entity_set:
                entity = entity_line.split("|")[0]
                data["tf"][entity] = data["tf"].get(entity, 0) + 1
            json.dump(data, open(path, "w", encoding="utf-8"))
            print("Learn the user profile.")
        else:
            print("No any entity")

    def _exec(self):
        while True:
            item = self.queue.get()
            self._learn(item["url"], item["ps"], item["user_id"])

    def learn(self, url, ps, user_id):
        self.queue.put({
            "url": url,
            "ps": ps,
            "user_id": user_id
        })
