#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把某层的新词条追加进 tools/oxford3000.txt（例句扩展词表）。"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    layer = sys.argv[1] if len(sys.argv) > 1 else "layer22.md"
    p = ROOT / "layers" / layer
    ws = []
    for line in p.read_text(encoding="utf-8").splitlines():
        m = re.match(
            r'^"([a-z]+(?:\s+[a-z]+)*)"\s+is\s+(?:a|an)\s+[a-z-]+\.$',
            line.strip(),
        )
        if m:
            ws.append(m.group(1))
    ox = ROOT / "tools" / "oxford3000.txt"
    lines = [x.strip() for x in ox.read_text(encoding="utf-8").splitlines()
             if x.strip() and not x.startswith("#")]
    new = [w for w in ws if w not in lines]
    text = ox.read_text(encoding="utf-8").rstrip()
    if new:
        text += "\n" + "\n".join(new) + "\n"
    ox.write_text(text, encoding="utf-8")
    print(f"层 {layer}: {len(ws)} 词条，新追加 {len(new)}；例句词表现共 {len(lines) + len(new)}")


if __name__ == "__main__":
    main()
