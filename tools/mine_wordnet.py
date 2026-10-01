#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordNet 词义挖掘器（离线，v0.1）
================================

数据源：Princeton WordNet 3.1（wn3.1.dict.tar.gz，约 16MB）。下载一次后永久
离线使用；文件放 work/wordnet.tar.gz，或解压目录 work/wordnet/dict/。
WordNet 数据许可证宽松，释义仅作草稿参考，改写进本项目后不随 App 分发原文。

挖掘逻辑：对每个目标词，取 WordNet 所有释义中“最短且每个词都属于当前词表”
的一条作为候选（词形变化自动归并，与 tools/check.py 同一套逻辑）。
找不到达标释义的词，会汇总它缺哪些支撑词 —— 决定下一批该先定义什么。

用法（在 english-bootstrap/ 目录下）:
    python tools/mine_wordnet.py             # 挖掘 tools/targets.txt
    python tools/mine_wordnet.py --words car window
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tarfile
from collections import Counter
from pathlib import Path

import check

ROOT = Path(__file__).resolve().parents[1]
WORK = Path(os.environ.get("BOOTSTRAP_WORK", str(ROOT.parent.parent / "work")))
POS_BY_FILE = {"noun": "noun", "verb": "verb", "adj": "adjective", "adv": "adverb"}


def ensure_dict_dir() -> Path | None:
    tar = WORK / "wordnet.tar.gz"
    for ddir in (WORK / "wordnet_nltk" / "wordnet",
                 WORK / "wordnet" / "dict"):
        if ddir.exists() and (ddir / "data.noun").exists():
            return ddir
    if tar.exists() and tar.stat().st_size > 16_000_000:
        with tarfile.open(tar) as t:
            t.extractall(WORK / "wordnet")
        d2 = WORK / "wordnet" / "dict"
        if (d2 / "data.noun").exists():
            return d2
    return None


def load_wordnet() -> dict[str, list[tuple[str, str]]]:
    ddir = ensure_dict_dir()
    if ddir is None:
        print("缺少 WordNet 数据：请先下载 wn3.1.dict.tar.gz（约16MB）放到 work/ 下。")
        return {}
    out: dict[str, list[tuple[str, str]]] = {}
    for fname, pos in POS_BY_FILE.items():
        for line in (ddir / f"data.{fname}").read_text(encoding="latin-1").splitlines():
            if " | " not in line:
                continue
            left, gloss = line.split(" | ", 1)
            fields = left.split()
            if len(fields) < 5:
                continue
            try:
                wcnt = int(fields[3])
            except ValueError:
                continue
            words = fields[4:4 + wcnt * 2:2]
            gloss = re.sub(r"\"[^\"]*\"", " ", gloss)  # 去掉例句引号
            gloss = re.sub(r"\s+", " ", gloss).strip().strip(";")
            if len(check.tokens(gloss)) < 3:
                continue
            for w in words:
                key = w.replace("_", " ").lower()
                out.setdefault(key, []).append((pos, gloss))
    return out


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

    allowed, phrases = set(), set()
    words, _ = check.load_layer0(False)
    allowed |= set(words)
    for i in range(1, 60):
        p = ROOT / "layers" / f"layer{i}.md"
        if p.exists():
            for e in check.parse_entries(p):
                (phrases if " " in e["word"] else allowed).add(e["word"])

    wn = load_wordnet()
    if not wn:
        return 1
    print(f"WordNet 就绪；当前词表 {len(allowed)} 词 + {len(phrases)} 词组；"
          f"目标 {len(targets)} 词")
    ok, miss = [], Counter()
    for w in targets:
        best = None
        for pos, gloss in wn.get(w, [])[:12]:
            if not bad_tokens(gloss, allowed, phrases):
                if best is None or len(gloss) < len(best[1]):
                    best = (pos, gloss)
        if best:
            ok.append((w, best[0], best[1]))
            print(f"  [OK] {w} ({best[0]}): {best[1]}")
        else:
            worst = Counter()
            for pos, gloss in wn.get(w, [])[:12]:
                for t in bad_tokens(gloss, allowed, phrases):
                    worst[t] += 1
            for t, n in worst.most_common(4):
                miss[t] += n
            print(f"  [--] {w}：缺 {', '.join(k for k, _ in worst.most_common(4)) or '无释义'}")
    print(f"\n达标 {len(ok)}/{len(targets)}")
    print("最常缺的支撑词（下一批优先补）：")
    for t, n in miss.most_common(20):
        print(f"  {t}  x{n}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
