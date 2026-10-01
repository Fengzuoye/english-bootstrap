#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对照官方牛津 3000 清单，输出尚未定义的剩余候选（按 CEFR A1→B2）。"""
import json
import re
from pathlib import Path

import check

ROOT = Path(__file__).resolve().parents[1]

BR_TO_US = {
    "behaviour": "behavior", "centre": "center", "colour": "color",
    "favourite": "favorite", "grey": "gray", "kilometre": "kilometer",
    "metre": "meter", "mum": "mom", "neighbour": "neighbor",
    "practise": "practice", "programme": "program", "theatre": "theater",
    "mum": "mom", "maths": "mathematics", "towards": "toward",
    "coloured": "colored", "favour": "favor", "neighbourhood": "neighborhood",
    "tyre": "tire", "judgement": "judgment", "defence": "defense",
    "licence": "license", "humour": "humor", "honour": "honor",
    "offence": "offense", "labour": "labor", "enquiry": "inquiry",
    "traveller": "traveler",
}


def defined_set():
    words, phrases = set(), set()
    l0, _ = check.load_layer0(False)
    words.update(l0)
    # 正式层
    files = [q for q in (ROOT / "layers").glob("layer*.md")
             if re.fullmatch(r"layer\d+\.md", q.name)]
    for p in sorted(files,
                    key=lambda q: (0, int(re.fullmatch(r"layer(\d+)\.md", q.name).group(1)))):
        for line in p.read_text(encoding="utf-8").splitlines():
            m = check.ENTRY_START_RE.match(line.strip())
            if m:
                w = m.group(1).lower()
                if " " in w or "-" in w:
                    phrases.add(w)
                else:
                    words.add(w)
    # 词组（如 be able to 之类条目也可能写作其它形式）
    return words, phrases


def norm(w: str) -> str:
    w = w.strip().strip("*").strip("(").strip(")")
    w = re.sub(r"\([^)]*\)", "", w).strip()
    return w.lower()


def main():
    words, phrases = defined_set()
    print(f"已定义: {len(words)} 词 + {len(phrases)} 词组")

    pkg = json.loads((ROOT / "tools" / ".." / ".." / ".." / "android-build" /
                      "package_cefr.json").read_text(encoding="utf-8"))
    remaining = []  # (level_order, word)
    order = {"A1": 0, "A2": 1, "B1": 2, "B2": 3}
    seen = set()
    for lv in ("A1", "A2", "B1", "B2"):
        for w in pkg.get(lv, []):
            n = norm(w)
            if n in seen:
                continue
            seen.add(n)
            if n in BR_TO_US and BR_TO_US[n] in words:
                continue
            spaced = n.replace("-", " ")
            if spaced in words or spaced in phrases:
                continue
            if n and n not in words and n not in phrases:
                remaining.append((order[lv], lv, n))
    remaining.sort()
    print(f"官方清单项: {len(seen)}，尚未定义: {len(remaining)}")
    for _, lv, w in remaining:
        print(f"{lv}\t{w}")
    out = ROOT / "tools" / "oxford_remaining.txt"
    with out.open("w", encoding="utf-8") as f:
        f.write("# 牛津 3000 尚未自举的候选词（CEFR A1→B2 近似高频优先）\n")
        for _, lv, w in remaining:
            f.write(f"{lv}\t{w}\n")
    print("saved", out)


if __name__ == "__main__":
    main()
