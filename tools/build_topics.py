#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为词典词条生成浏览元数据：
- g: 是否属于牛津 3000（官方清单，美式拼写归并）
- t: 语义范畴 id（WordNet 词法域映射）
- r: 词频次序（SemCor 计数为主，CEFR A1→B2 为兜底）

输出：{word: (g, t, r)}，由 export_dict.py 合并进 dict.json。
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = Path(os.environ.get("BOOTSTRAP_WORK", str(ROOT.parent.parent / "work")))
PKG = ROOT.parent.parent / "android-build" / "package_cefr.json"

BR_TO_US = {
    "behaviour": "behavior", "centre": "center", "colour": "color",
    "favourite": "favorite", "grey": "gray", "kilometre": "kilometer",
    "metre": "meter", "mum": "mom", "neighbour": "neighbor",
    "practise": "practice", "programme": "program", "theatre": "theater",
    "maths": "mathematics", "towards": "toward", "coloured": "colored",
    "favour": "favor", "neighbourhood": "neighborhood", "tyre": "tire",
    "judgement": "judgment", "defence": "defense", "licence": "license",
    "humour": "humor", "honour": "honor", "offence": "offense",
    "labour": "labor", "enquiry": "inquiry", "traveller": "traveler",
}

# WordNet lexnames 文件顺序即 lex_filenum 索引
LEXNAME = [
    "adj.all", "adj.pert", "adv.all", "noun.Tops", "noun.act", "noun.animal",
    "noun.artifact", "noun.attribute", "noun.body", "noun.cognition",
    "noun.communication", "noun.event", "noun.feeling", "noun.food",
    "noun.group", "noun.location", "noun.motive", "noun.object",
    "noun.person", "noun.phenomenon", "noun.plant", "noun.possession",
    "noun.process", "noun.quantity", "noun.relation", "noun.shape",
    "noun.state", "noun.substance", "noun.time", "verb.body", "verb.change",
    "verb.cognition", "verb.communication", "verb.competition",
    "verb.consumption", "verb.contact", "verb.creation", "verb.emotion",
    "verb.motion", "verb.perception", "verb.possession", "verb.social",
    "verb.stative", "verb.weather", "adj.ppl",
]

CAT_BY_LEX = {
    "noun.person": "person", "noun.animal": "animal", "noun.plant": "plant",
    "noun.food": "food", "noun.body": "body", "noun.artifact": "object",
    "noun.location": "place", "noun.time": "time", "noun.phenomenon": "nature",
    "noun.substance": "material", "noun.object": "object",
    "noun.group": "group", "noun.communication": "language",
    "noun.cognition": "mind", "noun.feeling": "feeling",
    "noun.event": "event", "noun.act": "action", "noun.state": "state",
    "noun.attribute": "quality", "noun.shape": "shape",
    "noun.quantity": "quantity", "noun.possession": "money",
    "noun.relation": "relation", "noun.motive": "mind", "noun.process": "action",
    "noun.Tops": "state", "verb.*": "action", "adj.all": "quality",
    "adj.pert": "quality", "adj.ppl": "quality", "adv.all": "time",
}

CATS = [
    ("action", "动作行为"), ("animal", "动物"), ("body", "身体"),
    ("event", "事件"), ("feeling", "情感"), ("food", "食物饮料"),
    ("function", "功能词"), ("group", "群体组织"), ("language", "语言沟通"),
    ("material", "材料物质"), ("mind", "知识与思想"), ("money", "金钱财物"),
    ("nature", "自然现象"), ("object", "物品工具"), ("person", "人物"),
    ("place", "地点场所"), ("plant", "植物"), ("quality", "性质描述"),
    ("quantity", "数量"), ("relation", "关系"), ("shape", "形状"),
    ("state", "状态"), ("time", "时间"),
]
CAT_NAME = dict(CATS)

FUNC_POS = {"pronoun", "article", "determiner", "conjunction",
            "preposition", "modal", "interjection", "auxiliary", "number"}


def load_official():
    """官方牛津 3000（A1→B2 顺序），返回 {词: 顺序}。"""
    pkg = json.loads(PKG.read_text(encoding="utf-8"))
    out = {}
    order = {"A1": 0, "A2": 1, "B1": 2, "B2": 3}
    idx = 0
    for lv in ("A1", "A2", "B1", "B2"):
        for w in pkg.get(lv, []):
            w = w.strip().lower()
            if w and w not in out:
                out[w] = (order[lv], idx)
                idx += 1
    return out


def is_official(w: str, official: dict) -> bool:
    if w in official:
        return True
    if w in BR_TO_US and BR_TO_US[w] in official:
        return True
    spaced = w.replace("-", " ")
    return spaced in official or spaced.replace("-", " ") in official


def load_wordnet_senses():
    ddir = WORK / "wordnet_nltk" / "wordnet"
    senses = {}  # lemma -> [lex_filenum...]
    if not (ddir / "data.noun").exists():
        return senses
    for fname, pos in (("data.noun", "n"), ("data.verb", "v"),
                       ("data.adj", "a"), ("data.adv", "r")):
        for line in (ddir / fname).read_text(encoding="latin-1").splitlines():
            if " | " not in line:
                continue
            left = line.split(" | ", 1)[0]
            fields = left.split()
            try:
                lex = int(fields[1])
            except (ValueError, IndexError):
                continue
            try:
                wcnt = int(fields[3])
            except (ValueError, IndexError):
                continue
            for i in range(4, 4 + wcnt * 2, 2):
                lemma = fields[i].replace("_", " ").lower()
                senses.setdefault(lemma, []).append((pos, lex))
    return senses


def load_counts():
    c = {}
    f = WORK / "wordnet_nltk" / "wordnet" / "cntlist.rev"
    if f.exists():
        for line in f.read_text(encoding="latin-1").splitlines():
            parts = line.split()
            if len(parts) == 2:
                try:
                    c[parts[0].lower()] = int(parts[1])
                except ValueError:
                    pass
    return c


def pick_cat(w: str, pos: str, senses: dict) -> str:
    if pos in FUNC_POS:
        return "function"
    cands = senses.get(w, [])
    if not cands:
        return "action" if pos == "verb" else "quality"
    # 优先名词域，其次动词域，最后形/副词域；取扫描中最常见的词义域
    for want in ("n", "v", "a", "r"):
        for p, lex in cands:
            if p != want:
                continue
            name = LEXNAME[lex] if lex < len(LEXNAME) else "noun.Tops"
            for cat in (name, "verb.*" if p == "v" else "noun.Tops"):
                if cat in CAT_BY_LEX:
                    return CAT_BY_LEX[cat]
    return "quality"


def cat_of_lex(lex: int | None, pos: str) -> str:
    if lex is not None and lex < len(LEXNAME):
        name = LEXNAME[lex]
        if name in CAT_BY_LEX:
            return CAT_BY_LEX[name]
        if name.startswith("verb."):
            return "action"
    return {"noun": "state", "verb": "action",
            "adjective": "quality", "adverb": "time"}.get(pos, "state")


def annotate(words: list[dict]) -> list[dict]:
    """words: export_dict 词条列表（就地补充 g/t/r），返回范畴顺序表。"""
    official = load_official()
    senses = load_wordnet_senses()
    counts = load_counts()
    cefr_index = {}
    for i, w in enumerate(official):
        cefr_index[w] = i

    metas = {}
    for e in words:
        w = e["w"]
        pos = e.get("pos", "noun")
        cat = pick_cat(w, pos, senses)
        g = 1 if is_official(w, official) else 0
        cnt = counts.get(w, 0)
        cidx = cefr_index.get(w, cefr_index.get(BR_TO_US.get(w), 10**9))
        if g == 0:
            cidx = 10**9 + len(metas)
        metas[w] = {"g": g, "t": cat, "c": cnt, "i": cidx}

    # 全局词频次序：SemCor 计数降序 → CEFR 序升序 → 字母序
    ordered = sorted(words, key=lambda e: (
        -(metas[e["w"]]["c"]), metas[e["w"]]["i"], e["w"]))
    for rank, e in enumerate(ordered):
        metas[e["w"]]["r"] = rank

    for e in words:
        m = metas[e["w"]]
        e["g"] = m["g"]
        e["t"] = m["t"]
        e["r"] = m["r"]

    topics = []
    for cid, name in CATS:
        n = sum(1 for e in words if e["t"] == cid)
        topics.append({"id": cid, "name": name, "n": n})
    return [t for t in topics if t["n"] > 0]
