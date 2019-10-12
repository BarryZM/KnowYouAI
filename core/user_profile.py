import json
import os
import config
from util.entity_tool import EntityObj


class UserProfile:
    # TODO 除了用户的频繁词，还有平凡调用的功能也要记录
    def __init__(self):
        self.userid_user_profile = {}
        self.userid_update = {}  # 每个user id更新的次数，更新一定次数后，定期序列化

    def load(self, user_id):
        if user_id not in self.userid_user_profile:
            dir_ = "./UserData/{}".format(user_id)
            path = "./UserData/{}/user_profile.json".format(user_id)
            if not os.path.exists(dir_):
                os.makedirs(dir_)
            if not os.path.exists(path):
                json.dump({
                    "tf": {},  # 实体频率，不需要tf-idf了
                    "count": 0,
                    "attitude": {},  # entity-like/unlike/normal
                    # "frequently_entity": set()  # 某些特定的实体（可以附上喜欢/不喜欢的实体）
                }, open(path, "w", encoding="utf-8"))
            user_profile = json.load(open(path, "r", encoding="utf-8"))
            self.userid_user_profile[user_id] = user_profile
            self.userid_update[user_id] = 0

    def get(self, key, user_id, default=None):
        self.load(user_id)
        user_profile = self.userid_user_profile[user_id]
        return user_profile.get(key, default)

    def write_pair(self, user_id, key, value):
        self.load(user_id)
        user_profile = self.userid_user_profile[user_id]
        user_profile[key] = value
        path = "./UserData/{}/user_profile.json".format(user_id)
        json.dump(user_profile, open(path, "w", encoding="utf-8"))

    def get_frequently_entity(self, user_id, n=10):
        self.load(user_id)
        user_profile = self.userid_user_profile[user_id]
        entity_tf = user_profile["tf"]
        entity = sorted(entity_tf, key=lambda x: entity_tf[x], reverse=True)
        if len(entity) > n:
            entity = entity[:n]
        return entity

    def entity_no_attitude(self, user_id):
        self.load(user_id)
        user_profile = self.userid_user_profile[user_id]
        entity_tf = user_profile["tf"]
        result = []
        for entity in entity_tf:
            if entity not in user_profile["attitude"]:
                result.append(entity)
        return result

    def update_attitude(self, user_id, attitude):
        self.load(user_id)

        for key in attitude:
            if key not in self.userid_user_profile[user_id]["attitude"]:
                self.userid_user_profile[user_id]["attitude"][key] = attitude[key]
                self.userid_update[user_id] += 1
                if (self.userid_update[user_id] + 1) % 3 == 0:
                    # print("Update user profile. ID:{}".format(user_id))
                    path = "./UserData/{}/user_profile.json".format(user_id)
                    json.dump(self.userid_user_profile[user_id], open(path, "w", encoding="utf-8"))

    def update(self, pos_seg, entitys, user_id):
        self.load(user_id)
        user_profile = self.userid_user_profile[user_id]
        entity_set = set()
        for item in entitys:
            if isinstance(item, EntityObj):
                entity_set.add(item.entity)
        for i, (word, tag) in enumerate(pos_seg):
            if "n" in tag:
                entity_set.add("n")
            if "nr" in tag:
                if len(word) > 1:
                    entity_set.add(word)
                if len(word) == 1 and (i + 1) != len(pos_seg):
                    word_, _ = pos_seg[i + 1]
                    word = word + word_
                    entity_set.add(word)
        for entity in entity_set:
            user_profile["tf"][entity] = user_profile["tf"].get(entity, 0) + 1

        user_profile["count"] += 1
        self.userid_update[user_id] += 1
        # print(self.userid_update[user_id])
        if (self.userid_update[user_id] + 1) % config.USER_PROFILE_UPDATE_ITER == 0:
            path = "./UserData/{}/user_profile.json".format(user_id)
            json.dump(user_profile, open(path, "w", encoding="utf-8"))
