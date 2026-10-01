#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查询一组词是否已进入允许词表（含第 0 层与全部正式层）。"""
import sys
from pathlib import Path

import check

ROOT = Path(__file__).resolve().parents[1]


def main():
    l0, _ = check.load_layer0(False)
    allowed = set(l0)
    phrases = set()
    files = [p for p in (ROOT / "layers").glob("layer*.md")
             if p.name[5:-3].isdigit() and p.name[5:-3] != ""]
    for p in sorted(files, key=lambda q: int(q.stem[5:])):
        for line in p.read_text(encoding="utf-8").splitlines():
            m = check.ENTRY_START_RE.match(line.strip())
            if m:
                w = m.group(1)
                if " " in w or "-" in w:
                    phrases.add(w)
                else:
                    allowed.add(w)
    for arg in sys.argv[1:]:
        for w in arg.split():
            print(f"{w}: {'OK' if w in allowed else 'NO'}"
                  + (f" (词组)" if w in phrases else ""))


if __name__ == "__main__":
    main()
