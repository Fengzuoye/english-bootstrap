#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 WordNet 3.1 生成“一般词”离线英英词典（全量 lemma）。
每词附带：中等详细度的释义 + 第一条例句 + 大范畴 t + 小情景 s。
小情景对动物/植物/人物/性状做了细分，物品地点等用释义关键词判断情景。
"""
import json
import os
import re
from pathlib import Path

import build_topics
import phonetics

ROOT = Path(__file__).resolve().parents[1]
WORK = Path(os.environ.get("BOOTSTRAP_WORK", str(ROOT.parent.parent / "work")))
DDIR = WORK / "wordnet_nltk" / "wordnet"
POS_FILE = {"noun": "data.noun", "verb": "data.verb",
            "adjective": "data.adj", "adverb": "data.adv"}

SCEN_NAME = {
    # 动作类（动词词法域）
    "bodyaction": "身体动作", "change": "变化过程", "thinking": "思考认知",
    "speaking": "言语交流", "sports": "运动比赛", "eating": "吃喝餐饮",
    "contact": "接触操作", "making": "制造创造", "feel": "情绪感受",
    "movement": "运动位移", "seeing": "感知观察", "owning": "占有得失",
    "social": "社交往来", "stateverbs": "存在状态", "weather": "天气",
    # 名词类
    "people": "人物身份", "animals": "动物", "plants": "植物",
    "fooddrink": "食物饮料", "bodyhealth": "身体医疗", "objects": "物品物件",
    "places": "地点场所", "time": "时间", "nature": "自然现象",
    "materials": "材料物质", "groups": "群体组织", "language": "语言文字",
    "mind": "知识与思想", "feelings": "情感", "events": "事件",
    "actions": "行为活动", "states": "状态", "quality": "性质",
    "shapes": "形状", "quantity": "数量", "money": "金钱财物",
    "relations": "关系", "other": "其它",
    # 性状描述细分
    "describing": "其它描述", "advword": "时间方式",
    "color": "颜色外观", "size": "大小多少", "speed": "快慢速度",
    "temperature": "冷热温度", "difficulty": "难易程度", "value": "贵贱价值",
    "emotionadj": "情绪形容", "taste": "味道口感", "sound": "声音",
    # 动物细分
    "pet": "宠物家养", "farm": "农场家畜", "wildmammal": "野生哺乳动物",
    "bird": "鸟类", "fishwater": "鱼类水生", "insect": "昆虫",
    "reptile": "爬行两栖", "animalother": "其它动物",
    # 植物细分
    "tree": "树木", "flower": "花卉", "foodcrop": "食用作物",
    "plantother": "其它植物",
    # 人物身份细分
    "occupation": "职业职位", "famrole": "家庭关系", "religionperson": "宗教人物",
    "ethnic": "民族地域", "agegender": "年龄性别", "socialrole": "社会身份",
    "personother": "其它身份",
    # 场景关键词细分
    "travel": "旅行交通", "school": "学校学习", "work": "工作职场",
    "sport": "运动比赛", "shopping": "购物消费", "home": "家居生活",
    "art": "艺术娱乐", "tech": "科技数码", "transport": "出行工具",
    "outdoor": "自然户外", "society": "法律社会", "family": "家庭人际",
}

LEX_SCEN = {
    "verb.body": "bodyaction", "verb.change": "change",
    "verb.cognition": "thinking", "verb.communication": "speaking",
    "verb.competition": "sports", "verb.consumption": "eating",
    "verb.contact": "contact", "verb.creation": "making",
    "verb.emotion": "feel", "verb.motion": "movement",
    "verb.perception": "seeing", "verb.possession": "owning",
    "verb.social": "social", "verb.stative": "stateverbs",
    "verb.weather": "weather",
    "adj.all": "describing", "adj.pert": "describing", "adj.ppl": "describing",
    "adv.all": "advword",
    "noun.person": "people", "noun.animal": "animals", "noun.plant": "plants",
    "noun.food": "fooddrink", "noun.body": "bodyhealth",
    "noun.artifact": "objects", "noun.location": "places", "noun.time": "time",
    "noun.phenomenon": "nature", "noun.substance": "materials",
    "noun.object": "objects", "noun.group": "groups",
    "noun.communication": "language", "noun.cognition": "mind",
    "noun.feeling": "feelings", "noun.event": "events", "noun.act": "actions",
    "noun.state": "states", "noun.attribute": "quality",
    "noun.shape": "shapes", "noun.quantity": "quantity",
    "noun.possession": "money", "noun.relation": "relations",
    "noun.Tops": "states", "noun.motive": "mind",
}


def _has(hay, words):
    return any((" " + k) in (" " + hay) for k in words)


def animal_scen(w, gloss):
    h = (w + " " + gloss).lower()
    if _has(h, ("fish", "aquatic", "shark", "salmon", "squid", "octopus", "whale",
                "dolphin", "sea", "water-dwelling", "gills")):
        return "fishwater"
    if _has(h, ("bird", "wing", "feather", "beak", "claw", "owl", "eagle", "sparrow",
                "pigeon", "waterfowl")):
        return "bird"
    if _has(h, ("insect", "bug", "ant", "bee", "beetle", "mosquito", "spider",
                "wings", "larva")):
        return "insect"
    if _has(h, ("snake", "lizard", "turtle", "crocodile", "frog", "toad",
                "reptile", "amphibian", "salamander")):
        return "reptile"
    if _has(h, ("domestic", "pet", "tame", "cat", "dog", "rabbit", "hamster",
                "parrot", "canary", "goldfish")):
        return "pet"
    if _has(h, ("farm", "cattle", "cow", "pig", "sheep", "goat", "horse",
                "donkey", "mule", "barnyard", "raised for", "beef", "milk",
                "duck", "goose", "chicken", "fowl")):
        return "farm"
    if _has(h, ("mammal", "carnivore", "herbivore", "primate", "rodent", "lion",
                "tiger", "bear", "wolf", "fox", "deer", "elephant", "monkey",
                "squirrel", "bat", "mouse", "rat", "wild")):
        return "wildmammal"
    return "animalother"


def plant_scen(w, gloss):
    h = (w + " " + gloss).lower()
    if _has(h, ("tree", "timber", "wood", "trunk", "conifer", "oak", "pine",
                "maple", "shrub", "bush")):
        return "tree"
    if _has(h, ("flower", "blossom", "bloom", "rose", "tulip", "orchid",
                "petal", "garden flower")):
        return "flower"
    if _has(h, ("crop", "vegetable", "food", "fruit", "edible", "bean", "rice",
                "wheat", "corn", "potato", "cabbage", "cultivated for food",
                "garden", "cultivate")):
        return "foodcrop"
    return "plantother"


def person_scen(w, gloss):
    h = (w + " " + gloss).lower()
    if _has(h, ("teacher", "doctor", "nurse", "soldier", "officer", "worker",
                "manager", "artist", "writer", "singer", "dancer", "player",
                "actor", "salesman", "policeman", "scientist", "pilot", "cook",
                "barber", "lawyer", "judge", "priest", "minister", "engineer",
                "profession", "occupation", "one who", "person whose job",
                "works for", "official", "merchant", "craftsman", "farmer")):
        return "occupation"
    if _has(h, ("religious", "church", "clergy", "belief", "god", "holy",
                "worship", "christian", "muslim", "jew", "buddhist", "saint")):
        return "religionperson"
    if _has(h, ("mother", "father", "parent", "son", "daughter", "brother",
                "sister", "husband", "wife", "relative", "ancestor",
                "offspring", "kin", "child of", "family")):
        return "famrole"
    if _has(h, ("national", "nation", "country", "native", "race", "tribe",
                "ethnic", "citizen of", "from ", "inhabitant", "people of")):
        return "ethnic"
    if _has(h, ("boy", "girl", "man", "woman", "male", "female", "child",
                "elder", "adult", "youth", "old", "young")):
        return "agegender"
    if _has(h, ("king", "queen", "royal", "noble", "lord", "lady", "duke",
                "prince", "princess", "emperor", "ruler", "chief", "leader")):
        return "socialrole"
    return "personother"


QUALITY_SCEN = [
    ("color", "颜色外观", ("color", "light", "dark", "red", "blue", "green",
                           "yellow", "black", "white", "gray", "hair", "skin",
                           "visual", "appearance", "shade")),
    ("size", "大小多少", ("large", "small", "big", "long", "short", "thick",
                          "thin", "wide", "narrow", "height", "size", "tall",
                          "length", "amount", "many", "few")),
    ("speed", "快慢速度", ("fast", "slow", "quick", "speed", "rapid", "swift",
                           "hasty")),
    ("temperature", "冷热温度", ("cold", "hot", "warm", "cool", "temperature",
                                 "heat", "freez", "chill")),
    ("difficulty", "难易程度", ("difficult", "easy", "hard", "simple",
                               "complex", "tough", "challenging")),
    ("value", "贵贱价值", ("expensive", "cheap", "valuable", "worth", "cost",
                           "price", "precious", "valuable")),
    ("emotionadj", "情绪形容", ("happy", "sad", "angry", "afraid", "fear",
                               "joy", "upset", "glad", "anxious", "worried",
                               "excited", "pleased", "proud", "calm", "angry")),
    ("taste", "味道口感", ("taste", "sweet", "sour", "bitter", "salty",
                           "delicious", "flavor", "smooth", "crisp", "juicy")),
    ("sound", "声音", ("sound", "loud", "quiet", "noisy", "silent", "soft voice")),
]


def quality_scen(w, gloss):
    h = (w + " " + gloss).lower()
    for sid, name, keys in QUALITY_SCEN:
        if _has(h, keys):
            return sid
    return "describing"


KEY_SCEN = [
    ("fooddrink", ("food", "eat", "drink", "meal", "cook", "kitchen", "taste",
                   "dish", "soup", "fruit", "vegetable", "wine")),
    ("bodyhealth", ("body", "health", "doctor", "hospital", "medicine",
                    "disease", "illness", "sick", "pain", "blood", "bone",
                    "muscle", "heart", "brain")),
    ("travel", ("travel", "trip", "journey", "tourist", "road", "train",
                "station", "airport", "plane", "ship", "vehicle", "hotel")),
    ("school", ("school", "learn", "study", "teach", "teacher", "student",
                "lesson", "class", "exam", "university", "book", "read")),
    ("work", ("work", "job", "company", "business", "office", "employ",
              "manager", "boss", "salary", "worker")),
    ("sport", ("sport", "game", "play", "team", "ball", "race", "run", "swim",
               "win", "competition", "player")),
    ("shopping", ("shop", "buy", "sell", "money", "pay", "price", "cost",
                  "store", "market", "purchase")),
    ("home", ("house", "room", "home", "bed", "chair", "table", "door",
              "window", "floor", "kitchen", "furniture")),
    ("art", ("art", "music", "paint", "film", "song", "sing", "dance",
             "picture", "draw", "stage", "concert", "theater")),
    ("tech", ("computer", "phone", "internet", "electric", "machine",
              "digital", "screen", "software", "device")),
    ("transport", ("car", "bus", "bike", "bicycle", "wheel", "engine",
                   "drive", "fuel")),
    ("outdoor", ("tree", "plant", "animal", "bird", "flower", "water", "sea",
                 "rain", "wind", "mountain", "forest", "sky", "earth")),
    ("society", ("law", "police", "court", "government", "political", "crime",
                 "prison", "right", "citizen", "election")),
    ("family", ("family", "mother", "father", "child", "parent", "wife",
                "husband", "marry", "friend", "relative")),
]


def scenario_of(lexname: str, pos: str, w: str, gloss: str, t: str) -> str:
    if t == "animal":
        return animal_scen(w, gloss)
    if t == "plant":
        return plant_scen(w, gloss)
    if t == "person":
        return person_scen(w, gloss)
    if pos == "adjective":
        return quality_scen(w, gloss)
    if t in ("object", "place", "group"):
        h = (w + " " + gloss).lower()
        for sid, keys in KEY_SCEN:
            if _has(h, keys):
                return sid
    return LEX_SCEN.get(lexname, "other")


def main():
    existing = set()
    dest_dict = ROOT / "android" / "english-bootstrap-app" / "app" / "src" / "main" / "assets" / "dict.json"
    if dest_dict.exists():
        for e in json.loads(dest_dict.read_text(encoding="utf-8"))["words"]:
            existing.add(e["w"])

    senses = {}  # lemma -> {pos: [(clean_def, ex, lex)]}
    for pos, fname in POS_FILE.items():
        for line in (DDIR / fname).read_text(encoding="latin-1").splitlines():
            if " | " not in line:
                continue
            left, raw = line.split(" | ", 1)
            fields = left.split()
            if len(fields) < 5:
                continue
            try:
                wcnt = int(fields[3])
            except ValueError:
                continue
            exm = re.findall(r'"([^"]*)"', raw)
            gloss = re.sub(r'"[^"]*"', " ", raw)
            gloss = re.sub(r"\s+", " ", gloss).strip().strip(";").strip()
            gloss = "; ".join(p.strip().strip(";").strip()
                              for p in gloss.split(";") if p.strip())
            if not gloss:
                continue
            try:
                lex = int(fields[1])
            except ValueError:
                lex = None
            ex = ""
            if exm:
                ex = exm[0].strip()
            for i in range(4, 4 + wcnt * 2, 2):
                lemma = fields[i].replace("_", " ").lower()
                if re.fullmatch(r"[a-z]+(?:[ -][a-z]+)*", lemma):
                    senses.setdefault(lemma, {}).setdefault(pos, []).append((gloss, ex, lex))

    counts = {}
    sensef = DDIR / "index.sense"
    if sensef.exists():
        for line in sensef.read_text(encoding="latin-1").splitlines():
            p = line.split()
            if len(p) < 4:
                continue
            lemma = p[0].split("%", 1)[0].replace("_", " ").lower()
            if not re.fullmatch(r"[a-z]+(?:[ -][a-z]+)*", lemma):
                continue
            try:
                counts[lemma] = counts.get(lemma, 0) + int(p[3])
            except ValueError:
                pass

    cands = [w for w in senses if w not in existing]
    cands.sort(key=lambda w: (-counts.get(w, 0), w))
    words = []
    ipa = phonetics.load()
    img_path = ROOT / "tools" / "image_keywords.json"
    img_kw = json.loads(img_path.read_text(encoding="utf-8")) if img_path.exists() else {}
    for w in cands:
        best = None  # (pos, score, def, ex, lex)
        for pos in ("noun", "verb", "adjective", "adverb"):
            for g, ex, lex in senses[w].get(pos, []):
                n = len(g.split())
                if n < 4 or n > 30:
                    continue
                score = abs(n - 16) - (0.2 if ex else 0)
                if best is None or score < best[1]:
                    best = (pos, score, g, ex, lex)
        if not best:
            continue
        t = build_topics.cat_of_lex(best[4], best[0])
        s = scenario_of(build_topics.LEXNAME[best[4]] if best[4] is not None else "",
                        best[0], w, best[2], t)
        entry = {
            "w": w, "pos": best[0], "def": best[2][:240],
            "ex": best[3][:160], "r": -counts.get(w, 0),
            "t": t, "s": s, "p": phonetics.ipa_for(w, ipa),
        }
        if w in img_kw:
            entry["ik"] = img_kw[w]
        words.append(entry)

    subs, seen_s = [], set()
    for e in words:
        if e["s"] not in seen_s:
            seen_s.add(e["s"])
            subs.append({"id": e["s"], "name": SCEN_NAME.get(e["s"], e["s"]),
                         "cat": e["t"]})

    dest = ROOT / "android" / "english-bootstrap-app" / "app" / "src" / "main" / "assets"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "general.json").write_text(
        json.dumps({"count": len(words), "words": words, "subs": subs},
                   ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8")
    print(f"一般词词典：{len(words)} 词，{len(subs)} 个小情景 -> {dest / 'general.json'}")


if __name__ == "__main__":
    main()
