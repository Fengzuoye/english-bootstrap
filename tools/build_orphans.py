#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补全“出现在释义/例句里、但词典没有收录”的低频词（如 allele 等学术词）。

流程：扫描 dict.json 的全部释义与例句 → 找缺失词元 → 从 WordNet 取释义
（放宽到 2–60 词，取最短合适义项）→ 追加进 general.json。
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
ASSETS = ROOT / "android" / "english-bootstrap-app" / "app" / "src" / "main" / "assets"
IRREGULAR = {"went": "go", "gone": "go", "teeth": "tooth", "feet": "foot",
             "children": "child", "men": "man", "women": "woman", "mice": "mouse",
             "was": "be", "were": "be", "is": "be", "are": "be", "been": "be",
             "has": "have", "had": "have", "did": "do", "does": "do", "done": "do",
             "better": "good", "best": "good", "worse": "bad", "worst": "bad"}


def tokens(text):
    return [t.lower() for t in re.findall(r"[A-Za-z][A-Za-z'-]*", text or "")]


def base_forms(w):
    out = {w}
    if w in IRREGULAR:
        out.add(IRREGULAR[w])
    for suf, rep in (("ies", "y"), ("es", ""), ("s", ""), ("ing", ""), ("ed", ""),
                     ("er", ""), ("est", "")):
        if w.endswith(suf) and len(w) > len(suf) + 1:
            out.add(w[: -len(suf)] + rep)
    return out


def main():
    dict_words = json.loads((ASSETS / "dict.json").read_text(encoding="utf-8"))["words"]
    general = json.loads((ASSETS / "general.json").read_text(encoding="utf-8"))
    known = set()
    for e in dict_words + general["words"]:
        known.add(e["w"])
    known |= {w.replace(" ", "") for w in known}

    missing = set()
    for e in dict_words + general["words"]:
        for text in (e.get("def", ""), e.get("ex", "")):
            for t in tokens(text):
                if t in known:
                    continue
                if base_forms(t) & known:
                    continue
                if t in IRREGULAR:
                    continue
                missing.add(t)
    print("缺失词元", len(missing), sorted(missing))

    # 读 WordNet（放宽长度限制）
    senses = {}
    for pos, fname in POS_FILE.items():
        for line in (DDIR / fname).read_text(encoding="latin-1").splitlines():
            if " | " not in line:
                continue
            left, raw = line.split(" | ", 1)
            f = left.split()
            if len(f) < 5:
                continue
            try:
                wcnt = int(f[3])
                lex = int(f[1])
            except ValueError:
                continue
            exm = re.findall(r'"([^"]*)"', raw)
            gloss = re.sub(r'"[^"]*"', " ", raw)
            gloss = "; ".join(p.strip().strip(";").strip()
                              for p in gloss.split(";") if p.strip())
            if not gloss:
                continue
            for i in range(4, 4 + wcnt * 2, 2):
                lemma = f[i].replace("_", " ").lower()
                if re.fullmatch(r"[a-z]+(?:[ -][a-z]+)*", lemma):
                    senses.setdefault(lemma, {}).setdefault(pos, []).append(
                        (gloss, exm[0] if exm else "", lex))

    ipa = phonetics.load()
    added = []
    added_words = set()
    for tok in sorted(missing):
        lemma = None
        for cand_w in [tok] + [b for b in base_forms(tok) if b != tok]:
            if cand_w in senses and cand_w not in known and cand_w not in added_words:
                lemma = cand_w
                break
        if lemma is None:
            continue
        w = lemma
        cands = senses[w]
        best = None
        for pos in ("noun", "verb", "adjective", "adverb"):
            for g, ex, lex in cands.get(pos, []):
                n = len(g.split())
                if n < 2 or n > 60:
                    continue
                score = abs(n - 14) - (0.3 if ex else 0)
                if best is None or score < best[1]:
                    best = (pos, score, g, ex, lex)
        if not best:
            continue
        t = build_topics.cat_of_lex(best[4], best[0])
        added.append({
            "w": w, "pos": best[0], "def": best[2][:240], "ex": best[3][:160],
            "r": 10 ** 9, "t": t, "s": build_topics.cat_of_lex(best[4], best[0]),
            "p": phonetics.ipa_for(w, ipa), "o": 1,
        })
        added_words.add(w)
    general["words"].extend(added)
    general["count"] = len(general["words"])
    (ASSETS / "general.json").write_text(
        json.dumps(general, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8")
    unresolved = [w for w in sorted(missing) if w not in {e["w"] for e in added}]
    print("未能在 WordNet 找到的缺失词：", unresolved)
    print(f"补入 {len(added)} 个低频词 -> general.json（总计 {general['count']}）")
    for e in added[:10]:
        print("  ", e["w"], "|", e["def"][:60])


if __name__ == "__main__":
    main()
