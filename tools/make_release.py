#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""整理最终发布目录（english-bootstrap-v1.4）并打包 zip。"""
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_SRC = ROOT / "release" / "english-bootstrap"       # README / LICENSE / NOTICE / scripts
REL = ROOT / "release" / "english-bootstrap-v1.4"
EXCLUDE_TOOLS = {"数值计算说明.txt", "app_numeric_logic.js", "oxford_remaining.txt"}


def cp_files(src, dst, patterns, exclude=()):
    dst.mkdir(parents=True, exist_ok=True)
    n = 0
    for p in sorted(src.iterdir()) if src.exists() else []:
        if p.is_file() and any(p.match(x) for x in patterns) and p.name not in exclude:
            shutil.copy2(p, dst / p.name)
            n += 1
    return n


def cp_tree(src, dst):
    n = 0
    for p in sorted(src.rglob("*")) if src.exists() else []:
        if p.is_dir() or any(x in p.parts for x in ("__pycache__", ".gradle", "build")):
            continue
        out = dst / p.relative_to(src)
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, out)
        n += 1
    return n


def main():
    print("docs:", cp_files(DOC_SRC, REL, ["README.md", "LICENSE", "NOTICE.md", ".gitignore"]))
    print("scripts:", cp_files(DOC_SRC / "scripts", REL / "scripts", ["*.py", "*.ps1"]))
    print("layers:", cp_files(ROOT / "layers", REL / "layers", ["*.md"]))
    print("tools:", cp_files(ROOT / "tools", REL / "tools",
                             ["*.py", "*.json", "*.txt"], exclude=EXCLUDE_TOOLS))
    app = ROOT / "android" / "english-bootstrap-app"
    print("android:", cp_tree(app, REL / "android" / "english-bootstrap-app"))
    assets = REL / "android" / "english-bootstrap-app" / "app" / "src" / "main" / "assets"
    if assets.exists():
        for p in assets.glob("*.json"):
            p.unlink()
    print("read:", cp_tree(ROOT / "read", REL / "read"))
    (REL / "dist").mkdir(parents=True, exist_ok=True)
    for name in ("EnglishBootstrapReader-v1.4.apk", "BootstrapReader-web.zip"):
        src = ROOT / "dist" / name
        if src.exists():
            shutil.copy2(src, REL / "dist" / name)
            print("dist:", name)

    full = ROOT / "dist" / "english-bootstrap-v1.4.zip"
    source = ROOT / "dist" / "english-bootstrap-v1.4-source.zip"
    with zipfile.ZipFile(full, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(REL.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(REL.parent))
    with zipfile.ZipFile(source, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(REL.rglob("*")):
            if p.is_file() and p.relative_to(REL).parts[0] != "dist":
                z.write(p, p.relative_to(REL.parent))
    # 旧文件名同步为干净内容，避免误拿旧包
    shutil.copy2(full, ROOT / "dist" / "english-bootstrap-github.zip")
    shutil.copy2(source, ROOT / "dist" / "english-bootstrap-source.zip")
    print("full:", full, full.stat().st_size)
    print("source:", source, source.stat().st_size)


if __name__ == "__main__":
    main()
