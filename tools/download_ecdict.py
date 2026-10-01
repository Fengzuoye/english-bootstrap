#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分块下载 ECDICT csv（用于补齐音标）。"""
import os
import time
import urllib.request
from pathlib import Path

WORK = Path(os.environ.get("BOOTSTRAP_WORK", str(Path(__file__).resolve().parents[2] / "work")))
URL = "https://raw.githubusercontent.com/skywind3000/ECDICT/master/ecdict.csv"
OUT = WORK / "ecdict.csv"


def fetch(start, end):
    req = urllib.request.Request(URL, headers={
        "User-Agent": "Mozilla/5.0", "Range": f"bytes={start}-{end}"})
    return urllib.request.urlopen(req, timeout=60).read()


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    head = fetch(0, 0)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0",
                                               "Range": "bytes=0-1"})
    resp = urllib.request.urlopen(req, timeout=60)
    total = int(resp.headers["Content-Range"].split("/")[-1])
    print("size", total)
    chunk = 2 << 20
    with open(OUT, "wb") as f:
        start = 0
        while start < total:
            end = min(start + chunk - 1, total - 1)
            for attempt in range(6):
                try:
                    data = fetch(start, end)
                    break
                except Exception as e:
                    print("retry", start, repr(e)[:80], flush=True)
                    time.sleep(2)
            else:
                raise RuntimeError(f"failed at {start}")
            f.write(data)
            start = end + 1
            if start % (10 << 20) < chunk:
                print(round(start * 100 / total), "%", flush=True)
    print("saved", OUT, os.path.getsize(OUT))


if __name__ == "__main__":
    main()
