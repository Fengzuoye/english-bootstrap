import re
from pathlib import Path
import check

ROOT = Path(__file__).resolve().parents[1]
tot = 0
for n in range(0, 22):
    if n == 0:
        continue
    p = ROOT / "layers" / f"layer{n}.md"
    if not p.exists():
        continue
    c = 0
    for line in p.read_text(encoding="utf-8").splitlines():
        if check.ENTRY_START_RE.match(line.strip()):
            c += 1
    tot += c
    print(n, c)
print("total", tot)
