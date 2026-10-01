#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""下载/准备外部数据源到 data_src/（WordNet 需手动下载）。"""
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data_src"

SOURCES = [
    ("cmudict.dict",
     "https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict"),
    ("ipa_en.txt",
     "https://cdn.jsdelivr.net/gh/open-dict-data/ipa-dict@master/data/en_US.txt"),
    ("package_cefr.json",
     "https://raw.githubusercontent.com/Kolia951/The_Oxford_3000_CEFR/main/package.txt"),
]


def fetch(url, dest):
    if dest.exists() and dest.stat().st_size > 1000:
        print("skip", dest.name)
        return
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, timeout=120).read()
    dest.write_bytes(data)
    print("saved", dest.name, len(data))


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    for name, url in SOURCES:
        try:
            fetch(url, DATA / name)
        except Exception as e:
            print("failed", name, e)
    print("""
还需要（手动下载）：
  WordNet 3.1: wn3.1.dict.tar.gz（约 16MB）
  解压后目录应为 data_src/wordnet_nltk/wordnet/data.noun 等文件。

构建时设置环境变量：
  Linux/macOS: export BOOTSTRAP_WORK=$(pwd)/data_src
  Windows:     $env:BOOTSTRAP_WORK="<repo>\\data_src"
""")


if __name__ == "__main__":
    main()
