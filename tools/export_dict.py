#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把当前全部层导出为 App 用词典 JSON（android/.../assets/dict.json）。"""
from __future__ import annotations

import json
import re
from pathlib import Path

import check
import build_topics
import phonetics

ROOT = Path(__file__).resolve().parents[1]


def load_layer0():
    words = []
    cur = None
    in_table = False
    for line in (ROOT / "layers" / "layer0.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            title = line[3:].strip()
            if "可降级" in title:
                break
            cur = title
            in_table = False
            continue
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        if cells[0] == "词" and cells[1] == "词性":
            in_table = True
            continue
        if not in_table:
            continue
        w, pos, gloss = cells[0].lower(), cells[1], cells[2]
        if re.fullmatch(r"[a-z]+", w) and pos in check.VALID_POS:
            words.append({"w": w, "pos": pos, "zh": gloss})
    return words


def load_entries(path):
    out = []
    cur = None
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        m = check.ENTRY_START_RE.match(s)
        if m:
            if cur:
                out.append(cur)
            cur = {"w": m.group(1), "pos": m.group(2).lower(), "def": "", "ex": ""}
            continue
        if cur is None:
            continue
        mm = check.MEANING_RE.match(s)
        if mm and mm.group(1) == cur["w"]:
            cur["def"] = mm.group(2)
            continue
        me = check.EXAMPLE_RE.match(s)
        if me:
            cur["ex"] = me.group(1)
    if cur:
        out.append(cur)
    return out


def main():
    words = []
    for w in load_layer0():
        words.append({"w": w["w"], "pos": w["pos"], "kind": "axiom",
                      "zh": w["zh"], "def": "（第 0 层公理词，直接记忆）", "ex": "",
                      "l": 0})
    def keyf(p):
        m = re.fullmatch(r"layer([1-9]\d*)\.md", p.name)
        return (0, int(m.group(1))) if m else (1, 0)
    files = [p for p in (ROOT / "layers").glob("layer*.md")
             if re.fullmatch(r"layer([1-9]\d*)\.md", p.name)]
    for p in sorted(files, key=keyf):
        layer_no = int(re.fullmatch(r"layer([1-9]\d*)\.md", p.name).group(1))
        for e in load_entries(p):
            words.append({"w": e["w"], "pos": e["pos"], "kind": "defined",
                          "def": e["def"], "ex": e["ex"], "l": layer_no})
    ext_path = ROOT / "tools" / "extended.json"
    if ext_path.exists():
        ext = json.loads(ext_path.read_text(encoding="utf-8"))
        by_word = {w["w"]: w for w in words}
        for w, detail in ext.items():
            if w in by_word:
                by_word[w]["ext"] = detail
            else:
                print(f"警告：extended.json 中 {w} 不在词典里，已跳过")
    topics = build_topics.annotate(words)
    ipa = phonetics.load()
    img_path = ROOT / "tools" / "image_keywords.json"
    img_kw = json.loads(img_path.read_text(encoding="utf-8")) if img_path.exists() else {}
    for e in words:
        e["p"] = phonetics.ipa_for(e["w"], ipa)
        if e["w"] in img_kw:
            e["ik"] = img_kw[e["w"]]
    dest = ROOT / "android" / "english-bootstrap-app" / "app" / "src" / "main" / "assets"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "dict.json").write_text(
        json.dumps({"count": len(words), "words": words, "topics": topics},
                   ensure_ascii=False, indent=0),
        encoding="utf-8")
    print(f"导出 {len(words)} 词 -> {dest / 'dict.json'}")


if __name__ == "__main__":
    main()
