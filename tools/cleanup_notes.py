#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""去掉层文件里的草稿注释行，并报告重复词条（供人工修正）。"""
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKERS = (
    "is not in list", "is already defined", "defined twice? skip",
    "is not chosen", "defined twice", "not in list",
)


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "layer27.md"
    p = ROOT / "layers" / name
    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
    keep = [ln for ln in lines if not any(m in ln for m in MARKERS)]
    p.write_text("".join(keep), encoding="utf-8")
    ws = []
    for line in p.read_text(encoding="utf-8").splitlines():
        m = re.match(r'^"([a-z ]+)" is (?:a|an) [a-z-]+\.$', line.strip())
        if m:
            ws.append(m.group(1))
    dups = [w for w, c in Counter(ws).items() if c > 1]
    print(f"清理后词条 {len(ws)}；重复: {dups}")


if __name__ == "__main__":
    main()
