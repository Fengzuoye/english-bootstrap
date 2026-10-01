#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统计已定义词/词组，并列出候选清单里尚未定义的项。"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def defined_words():
    words, phrases = set(), set()
    for p in sorted((ROOT / "layers").glob("layer*.md")):
        for line in p.read_text(encoding="utf-8").splitlines():
            m = re.match(r'^"([^"]+)" is a (noun|verb|adjective|adverb|preposition|conjunction|determiner|pronoun|number|exclamation)\.$', line.strip())
            if m:
                w = m.group(1)
                if " " in w or "-" in w:
                    phrases.add(w)
                else:
                    words.add(w)
    return words, phrases


def plain_lines(path):
    return [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.startswith("#")]


def main():
    words, phrases = defined_words()
    print(f"已定义：{len(words)} 词 + {len(phrases)} 词组")
    for name in ("oxford3000.txt", "targets.txt"):
        p = ROOT / "tools" / name
        if not p.exists():
            continue
        lines = plain_lines(p)
        undef = [w for w in lines if w not in words and w not in phrases]
        print(f"{name}: {len(lines)} 项，未定义 {len(undef)} 项")
        if name == "targets.txt":
            print("未定义 targets:", " ".join(undef))


if __name__ == "__main__":
    main()
