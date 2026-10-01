#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成可直接双击打开的网页版（file:// 也能用）。

把 dict/general/grammar 数据写成 classic <script src> 的 JS 文件，
并让页面优先使用 window.__DICT__ / __GENERAL__ / __GRAMMAR__。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "android" / "english-bootstrap-app" / "app" / "src" / "main" / "assets"
WEB = ROOT / "web"


def main():
    html = (ASSETS / "index.html").read_text(encoding="utf-8")
    html = html.replace(
        "function loadDict(){",
        "function loadDict(){ if(window.__DICT__){ DICTERROR=false; bootDict(window.__DICT__); return; }")
    html = html.replace(
        "function loadGeneral(){",
        "function loadGeneral(){ if(window.__GENERAL__){ GENERROR=false; bootGeneral(window.__GENERAL__); return; }")
    html = html.replace(
        "function loadGrammar(){",
        "function loadGrammar(){ if(window.__GRAMMAR__){ GRAMMAR=(window.__GRAMMAR__.topics)||[]; return; }")
    loader = ('<script src="data-dict.js"></script>\n'
              '<script src="data-general.js"></script>\n'
              '<script src="data-grammar.js"></script>\n'
              '<script>\n')
    html = html.replace("<script>\nvar DICT = {};", loader + "var DICT = {};", 1)
    WEB.mkdir(parents=True, exist_ok=True)
    (WEB / "index.html").write_text(html, encoding="utf-8")
    for src, var in (("dict.json", "__DICT__"), ("general.json", "__GENERAL__"),
                     ("grammar.json", "__GRAMMAR__")):
        data = json.loads((ASSETS / src).read_text(encoding="utf-8"))
        (WEB / ("data-" + src.replace(".json", ".js"))).write_text(
            "window." + var + "=" + json.dumps(data, ensure_ascii=False,
                                               separators=(",", ":")) + ";",
            encoding="utf-8")
    (WEB / "使用说明.txt").write_text(
        "双击 index.html 即可在电脑浏览器里使用（无需服务器）。\n"
        "数据已打包为同目录下的 data-*.js，可连同文件夹一起复制。\n"
        "手机浏览器也可打开，但功能与 Android 安装包一致。\n",
        encoding="utf-8")
    print("web 版已生成 ->", WEB)


if __name__ == "__main__":
    main()
