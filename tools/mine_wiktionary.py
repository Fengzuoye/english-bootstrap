#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wiktionary 词义挖掘器（v0.1，完全免费）
========================================

数据源：dictionaryapi.dev（Wiktionary 派生的公开 API，CC BY-SA，无需 key）。
墙内实测：dictionaryapi.dev 可达；en.wiktionary.org 不可达；kaikki.org 可达但
单词页约 1MB、全量转储 3GB，本工具不采用。

作用：对一批目标词，自动找出“释义里每个词都属于当前词表”的候选定义，
并统计差一点就达标时缺哪些支撑词 —— 直接告诉我们下一批该写什么、按什么顺序。

用法（在 english-bootstrap/ 目录下）:
    python tools/mine_wiktionary.py            # 挖掘 tools/targets.txt 里的词
    python tools/mine_wiktionary.py --words car window  # 或临时指定几个词

说明：挖掘结果是“草稿”，仍需改写成
    "word" is a noun. / The meaning of ... / Example: ...
    并交给 python tools/check.py 做最终校验。
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

import check  # 复用词表与词形归并逻辑

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "wiktionary_cache"
UA = {"User-Agent": "BootstrapMiner/0.1 (personal learning; CC BY-SA)"}
POS_MAP = {"numeral": "number", "verb": "verb", "noun": "noun",
           "adjective": "adjective", "adverb": "adverb",
           "preposition": "preposition", "conjunction": "conjunction",
           "pronoun": "pronoun", "interjection": "interjection",
           "determiner": "determiner"}
TAG_RE = re.compile(
    r"\((countable|uncountable|usually|often|transitive|intransitive|"
    r"informal|formal|dated|plural|singular|chiefly|rarely|rare|"
    r"chiefly|synonym[^)]*)\)", re.I)


def load_vocab() -> tuple[set[str], set[str]]:
    allowed, phrases = set(), set()
    words, _ = check.load_layer0(False)
    allowed |= set(words)
    for i in range(1, 60):
        p = ROOT / "layers" / f"layer{i}.md"
        if not p.exists():
            continue
        for e in check.parse_entries(p):
            w = e["word"]
            (phrases if " " in w else allowed).add(w)
    return allowed, phrases


def bad_tokens(text: str, allowed: set[str], phrases: set[str]) -> list[str]:
    t = text
    for ph in sorted(phrases, key=len, reverse=True):
        t = re.sub(r"(?<![a-z])" + re.escape(ph) + r"(?![a-z])", " ", t,
                   flags=re.IGNORECASE)
    out = []
    for tok in check.tokens(t):
        if tok in check.META_SYMBOLS:
            continue
        if not check.resolve(tok, allowed):
            out.append(tok)
    return out


def clean_def(s: str) -> str:
    s = s.replace("\n", " ")
    s = TAG_RE.sub(" ", s)
    s = s.strip().strip(".").strip()
    s = re.sub(r"\s+", " ", s)
    return s


def fetch(word: str) -> dict | None:
    cache = CACHE / f"{word}.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    url = "https://api.dictionaryapi.dev/api/v2/entries/en/" + urllib.parse.quote(word)
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=12) as r:
                data = json.loads(r.read().decode("utf-8"))
            CACHE.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps(data), encoding="utf-8")
            return data
        except Exception:
            if attempt == 0:
                time.sleep(1)
    return None


def candidates(word: str, data: dict | None) -> list[tuple[str, str]]:
    if not data or not isinstance(data, list):
        return []
    out = []
    for entry in data:
        for m in entry.get("meanings", []):
            pos = POS_MAP.get(m.get("partOfSpeech", "").lower())
            if not pos:
                continue
            for d in m.get("definitions", []):
                text = clean_def(d.get("definition", ""))
                if 3 <= len(check.tokens(text)) <= 40:
                    out.append((pos, text))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--words", nargs="*", default=None)
    args = ap.parse_args()
    if args.words:
        targets = args.words
    else:
        tf = ROOT / "tools" / "targets.txt"
        targets = [ln.strip() for ln in tf.read_text(encoding="utf-8").splitlines()
                   if ln.strip() and not ln.startswith("#")]

    allowed, phrases = load_vocab()
    print(f"当前词表：{len(allowed)} 词 + {len(phrases)} 词组，目标词 {len(targets)} 个")
    ok_lines, miss = [], Counter()
    results: dict[str, dict | None] = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        for w, data in zip(targets, ex.map(fetch, targets)):
            results[w] = data
    for i, w in enumerate(targets, 1):
        data = results.get(w)
        best = None
        for pos, text in candidates(w, data):
            if not bad_tokens(text, allowed, phrases):
                if best is None or len(text) < len(best[1]):
                    best = (pos, text)
        if best:
            ok_lines.append((w, best[0], best[1]))
            print(f"  [OK] {w} ({best[0]}): {best[1]}")
        elif data is None:
            print(f"  [??] {w}：抓取失败")
        else:
            worst = Counter()
            for pos, text in candidates(w, data):
                for t in bad_tokens(text, allowed, phrases):
                    worst[t] += 1
            for t, n in worst.most_common(4):
                miss[t] += n
            print(f"  [--] {w}：缺 {', '.join(k for k, _ in worst.most_common(4)) or '释义'}")

    print(f"\n达标 {len(ok_lines)}/{len(targets)}")
    print("最常缺的支撑词（下一批优先补这些）：")
    for t, n in miss.most_common(20):
        print(f"  {t}  x{n}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
