#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 markdown 层文件生成阅读友好的 HTML 文档。

用法（在 english-bootstrap/ 目录下）:
    python tools/build_read.py

输出:
    read/index.html          总览与导航
    read/layer0.html         第 0 层词表（卡片式，可搜索、可自测）
    read/layer1_preview.html 第 1 层预热（书籍式词条，可自测）

markdown 文件始终是唯一数据源；改完 md 后重新运行本脚本即可。
"""

from __future__ import annotations

import html as _html
import re
from pathlib import Path

import check  # 复用 md 解析逻辑

ROOT = Path(__file__).resolve().parents[1]
READ = ROOT / "read"
LAYER0_MD = ROOT / "layers" / "layer0.md"
LAYER1_MD = ROOT / "layers" / "layer1.md"
LAYER2_MD = ROOT / "layers" / "layer2.md"
PREVIEW_MD = ROOT / "layers" / "layer1_preview.md"


def esc(s: str) -> str:
    return _html.escape(s, quote=True)


def pretty_title(t: str) -> str:
    t = re.sub(r"^\d+\.\s*", "", t)
    t = re.sub(r"（.*）$", "", t)
    return t.strip()


CSS = """
:root{
  --bg:#f7f5f0; --card:#fffdf9; --ink:#2d2a26; --muted:#7a7267;
  --line:#e6dfd3; --accent:#1f6f6b; --accent-soft:#e4f0ee;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:"Segoe UI","PingFang SC","Microsoft YaHei",system-ui,sans-serif;
  line-height:1.8;}
.wrap{max-width:900px;margin:0 auto;padding:36px 22px 90px;}
h1{font-size:1.55rem;margin:6px 0 6px;letter-spacing:.01em;}
.subtitle{color:var(--muted);margin:0 0 26px;}
nav.top{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:24px;}
nav.top a{color:var(--accent);text-decoration:none;border:1px solid var(--line);
  background:var(--card);padding:5px 14px;border-radius:999px;font-size:.88rem;}
.note{background:#fff8e8;border:1px solid #ecd9a8;border-radius:12px;
  padding:14px 18px;font-size:.93rem;margin:18px 0;color:#5c4f33;}
.controls{position:sticky;top:0;background:var(--bg);padding:10px 0 12px;z-index:5;
  display:flex;gap:10px;flex-wrap:wrap;align-items:center;border-bottom:1px solid var(--line);}
.controls input[type=search]{flex:1;min-width:200px;padding:8px 12px;
  border:1px solid var(--line);border-radius:9px;background:var(--card);
  font-size:.95rem;font-family:inherit;}
.controls select{padding:8px 10px;border:1px solid var(--line);border-radius:9px;
  background:var(--card);font-size:.9rem;font-family:inherit;}
.controls label{font-size:.85rem;color:var(--muted);display:flex;gap:6px;align-items:center;
  white-space:nowrap;cursor:pointer;}
.cat{margin-top:36px;}
.cat h2{font-size:1.12rem;border-left:4px solid var(--accent);padding-left:10px;
  margin:0 0 14px;}
.cat h2 .count{color:var(--muted);font-weight:normal;font-size:.85rem;}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px;}
.chip{background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:12px 15px;box-shadow:0 1px 2px rgba(0,0,0,.04);}
.chip .word{font-family:Georgia,"Times New Roman",serif;font-size:1.3rem;}
.chip .gloss{color:var(--muted);font-size:.85rem;margin-top:2px;}
.badge{display:inline-block;font-size:.68rem;letter-spacing:.04em;padding:2px 9px;
  border-radius:999px;color:#fff;vertical-align:middle;font-family:inherit;}
.badge.noun{background:#2f6f6b}.badge.verb{background:#b3541e}
.badge.adjective{background:#8a5a9b}.badge.adverb{background:#4a6fa5}
.badge.pronoun{background:#7a7a52}.badge.article{background:#6b7280}
.badge.number{background:#2c7a3d}.badge.determiner{background:#a05a7c}
.badge.preposition{background:#5a7a9c}.badge.conjunction{background:#8a6d3b}
.badge.modal{background:#7a5a8a}.badge.interjection{background:#9c6b3c}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;
  padding:20px 24px;margin:18px 0;box-shadow:0 1px 3px rgba(0,0,0,.05);}
.card .entry-head{display:flex;justify-content:space-between;align-items:center;}
.card .num{color:var(--muted);font-size:.8rem;}
.card .word{font-family:Georgia,"Times New Roman",serif;font-size:1.55rem;
  margin:8px 0 10px;cursor:pointer;display:inline-block;}
.card .meaning{font-family:Georgia,"Times New Roman",serif;font-size:1.06rem;
  margin:0 0 8px;color:#34302b;}
.card .meaning q{background:var(--accent-soft);padding:2px 9px;border-radius:7px;}
.card .example{color:#4a453f;margin:0;font-style:italic;font-size:.98rem;}
.card .example b{font-weight:700;font-style:normal;}
.rule{color:#4a453f;margin:16px 0;padding-left:12px;border-left:3px solid #d9cfbf;
  font-size:.97rem;}
body.selftest .card .meaning, body.selftest .card .example{display:none;}
body.selftest .card.show .meaning, body.selftest .card.show .example{display:block;}
body.selftest .chip .gloss{display:none;}
body.selftest .chip.show .gloss{display:block;}
body.selftest .chip{cursor:pointer;}
.biglink{display:block;background:var(--card);border:1px solid var(--line);
  border-radius:14px;padding:18px 22px;margin:14px 0;text-decoration:none;
  color:var(--ink);box-shadow:0 1px 3px rgba(0,0,0,.05);}
.biglink:hover{border-color:var(--accent);}
.biglink .t{font-size:1.12rem;color:var(--accent);font-weight:600;}
.biglink .d{color:var(--muted);font-size:.9rem;margin-top:2px;}
section h2{margin-top:30px;font-size:1.12rem;}
ol,ul{padding-left:22px;}
@media (max-width:640px){
  .wrap{padding:12px 12px 120px}
  h1{font-size:1.3rem}
  .controls{padding:8px 2px 10px;gap:8px}
  .controls input[type=search]{padding:10px 12px;font-size:16px}
  .controls select{padding:10px 8px;font-size:16px}
  .controls label{font-size:15px}
  .card{padding:18px 16px;margin:10px 0;min-height:28vh;display:flex;
    flex-direction:column;justify-content:center;border-radius:16px}
  .card .word{font-size:1.7rem}
  .card .meaning{font-size:1.12rem}
  .card .example{font-size:1rem}
  .card .badge{font-size:.75rem;padding:3px 10px}
  .rule{font-size:1rem;line-height:1.7}
  .cat h2{font-size:1.15rem}
  .grid{grid-template-columns:repeat(auto-fill,minmax(148px,1fr));gap:10px}
  .chip{padding:14px;border-radius:14px}
  .chip .word{font-size:1.45rem}
  .chip .gloss{font-size:.95rem}
  .panel{max-height:55vh}
  .biglink{padding:18px 16px}
}
@media print{
  .controls,nav.top{display:none}
  body{background:#fff}
  .card,.chip{box-shadow:none}
}
"""


COMMON_JS = """
var q=document.getElementById('q');
var cat=document.getElementById('cat');
var selftest=document.getElementById('selftest');
function apply(){
  if(!q||!cat) return;
  var qv=q.value.trim().toLowerCase();
  var cv=cat.value;
  document.querySelectorAll('[data-search]').forEach(function(el){
    var ok=(!qv||el.getAttribute('data-search').indexOf(qv)>-1)&&(!cv||el.getAttribute('data-cat')===cv);
    el.style.display=ok?'':'none';
  });
  document.querySelectorAll('section.cat').forEach(function(sec){
    var any=false;
    sec.querySelectorAll('[data-search]').forEach(function(el){
      if(el.style.display!=='none'){any=true;}
    });
    sec.style.display=any?'':'none';
  });
}
if(q) q.addEventListener('input',apply);
if(cat) cat.addEventListener('change',apply);
if(selftest){
  selftest.addEventListener('change',function(){
    document.body.classList.toggle('selftest',selftest.checked);
  });
  document.querySelectorAll('.card .word,.chip').forEach(function(el){
    el.addEventListener('click',function(){el.classList.toggle('show');});
  });
}
"""


def nav_links() -> str:
    links = ['<a href="index.html">首页</a>', '<a href="layer0.html">词表</a>']
    for i in range(1, 40):
        if (ROOT / "layers" / f"layer{i}.md").exists():
            links.append(f'<a href="layer{i}.html">第 {i} 层</a>')
    links.append('<a href="layer1_preview.html">预热</a>')
    return "".join(links)


def page(title: str, subtitle: str, nav: str = "", controls: str = "",
         content: str = "", extra_js: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <nav class="top">{nav or nav_links()}</nav>
  <h1>{esc(title)}</h1>
  <p class="subtitle">{esc(subtitle)}</p>
  {controls}
  {content}
</div>
<script>{COMMON_JS}{extra_js}</script>
</body>
</html>
"""


def parse_layer0():
    """返回 (核心类别列表, 可选口语词类别)。"""
    cats: list[dict] = []
    optional = None
    cur: dict | None = None
    in_table = False
    for line in LAYER0_MD.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            title = line[3:].strip()
            if "可降级" in title:
                break
            cur = {"title": title, "words": []}
            in_table = False
            if "可选" in title:
                optional = cur
            else:
                cats.append(cur)
            continue
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        if cells[0] == "词" and cells[1] == "词性":
            in_table = True
            continue
        if not in_table:
            continue
        w, pos, gloss = cells[0], cells[1], cells[2]
        if not w or pos not in check.VALID_POS:
            continue
        cur["words"].append((w, pos, gloss))
    return cats, optional


def parse_layer_file(path: Path):
    """返回 [{title, prose: [...], entries: [...]}]，保留正文与词条的先后顺序。"""
    sections: list[dict] = []
    cur_sec: dict | None = None
    cur_entry: dict | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("## "):
            cur_sec = {"title": s[3:].strip(), "prose": [], "entries": []}
            sections.append(cur_sec)
            cur_entry = None
            continue
        if not s or s.startswith(("#", ">")):
            continue
        m = check.ENTRY_START_RE.match(s)
        if m:
            cur_entry = {"word": m.group(1), "pos": m.group(2).lower(),
                         "defs": [], "exs": []}
            if cur_sec is not None:
                cur_sec["entries"].append(cur_entry)
            continue
        if cur_entry is not None:
            mm = check.MEANING_RE.match(s)
            if mm and mm.group(1) == cur_entry["word"]:
                cur_entry["defs"].append(mm.group(2))
                continue
            me = check.EXAMPLE_RE.match(s)
            if me:
                cur_entry["exs"].append(me.group(1))
                continue
        if cur_sec is not None:
            cur_sec["prose"].append(s)
    return [sec for sec in sections if sec["prose"] or sec["entries"]]


def cat_options(sections: list[dict]) -> str:
    opts = ['<option value="">全部</option>']
    for i, sec in enumerate(sections):
        n = (len(sec.get("words", [])) + len(sec.get("entries", []))
             + len(sec.get("prose", [])))
        opts.append(f'<option value="c{i}">{esc(pretty_title(sec["title"]))}（{n}）</option>')
    return "".join(opts)


def controls_html(cat_id: str, selftest_hint: str, options: str) -> str:
    return f"""<div class="controls">
  <input id="q" type="search" placeholder="搜索词或释义…">
  <select id="{cat_id}">{options}</select>
  <label><input id="selftest" type="checkbox"> 自测模式</label>
</div>
<p class="note">{selftest_hint}</p>"""


def render_layer0() -> str:
    cats, optional = parse_layer0()
    sections = cats + ([optional] if optional else [])
    core = sum(len(c["words"]) for c in cats)
    opt_n = len(optional["words"]) if optional else 0

    def chip(w: str, pos: str, gloss: str, cat_i: int) -> str:
        return (f'<div class="chip" data-search="{esc(w)} {esc(pos)} {esc(gloss)}" '
                f'data-cat="c{cat_i}">'
                f'<div class="word">{esc(w)}</div>'
                f'<span class="badge {esc(pos)}">{esc(pos)}</span>'
                f'<div class="gloss">{esc(gloss)}</div></div>')

    body_parts: list[str] = []
    for i, sec in enumerate(sections):
        title = pretty_title(sec["title"])
        is_opt = "可选" in sec["title"]
        grid = "".join(chip(w, pos, g, i) for w, pos, g in sec["words"])
        label = f"{title}（可选）" if is_opt else f"{title}"
        body_parts.append(
            f'<section class="cat" id="cat-{i}">'
            f'<h2>{esc(label)} <span class="count">{len(sec["words"])} 词</span></h2>'
            f'<div class="grid">{grid}</div></section>')

    subtitle = f"公理层：共 {core} 词" + (f"（另有 {opt_n} 个可选口语词）" if opt_n else "")
    hint = ("第 0 层是公理层：这些词不定义，直接记忆。中文速记只在这里出现一次。"
            "打开“自测模式”，先看英文词、想中文意思，再点卡片看答案。")
    controls = controls_html("cat", hint, cat_options(sections))
    content = "".join(body_parts)
    return page("第 0 层 · 基础词表", subtitle, "", controls, content)


def layer0_core_count() -> int:
    cats, _ = parse_layer0()
    return sum(len(c["words"]) for c in cats)


def render_entries_page(path: Path, title: str, hint: str, subtitle_tpl: str) -> str:
    sections = parse_layer_file(path)
    total = sum(len(s["entries"]) for s in sections)
    core = layer0_core_count()
    idx = 0
    body_parts: list[str] = []
    for i, sec in enumerate(sections):
        parts: list[str] = []
        for p in sec["prose"]:
            parts.append(f'<p class="rule">{esc(p)}</p>')
        for e in sec["entries"]:
            idx += 1
            w, pos = e["word"], e["pos"]
            meaning = esc(e["defs"][0])
            ex = esc(e["exs"][0])
            ex_html = re.sub(rf"\b{re.escape(w)}\b", f"<b>{esc(w)}</b>",
                             ex, flags=re.IGNORECASE)
            parts.append(
                f'<article class="card" data-search="{esc(w)} {meaning} {ex}" data-cat="c{i}">'
                f'<div class="entry-head"><span class="badge {esc(pos)}">{esc(pos)}</span>'
                f'<span class="num">#{idx}</span></div>'
                f'<h3 class="word">{esc(w)}</h3>'
                f'<p class="meaning">The meaning of <q>{esc(w)}</q> is <q>{meaning}</q>.</p>'
                f'<p class="example">Example: “{ex_html}”</p>'
                f'</article>')
        n = len(sec["entries"]) + len(sec["prose"])
        body_parts.append(
            f'<section class="cat" id="cat-{i}">'
            f'<h2>{esc(pretty_title(sec["title"]))} <span class="count">{n}</span></h2>'
            + "".join(parts) + "</section>")
    controls = controls_html("cat", hint, cat_options(sections))
    return page(title, subtitle_tpl.format(total=total, core=core), "", controls,
                "".join(body_parts))


def render_preview() -> str:
    return render_entries_page(
        PREVIEW_MD, "第 1 层预热 · 机制演示",
        "这些词按顺序依赖前面的词。打开“自测模式”，先看词、想它的英语定义，再点词看答案。",
        "机制演示：{total} 个新词，全部只用第 0 层 {core} 词定义")


LAYER_TITLES = {
    1: "第 1 层 · 词性与最基础语法",
    2: "第 2 层 · 高中到大一全部常用语法",
    3: "第 3 层 · 牛津3000 第1批",
    4: "第 4 层 · 牛津3000 第2批",
    5: "第 5 层 · 牛津3000 第3批",
    6: "第 6 层 · 牛津3000 第4批",
    7: "第 7 层 · 牛津3000 第5批",
    8: "第 8 层 · 牛津3000 第6批",
    9: "第 9 层 · 牛津3000 第7批",
    10: "第 10 层 · 牛津3000 第8批",
    11: "第 11 层 · 牛津3000 第9批",
    12: "第 12 层 · 牛津3000 第10批",
    13: "第 13 层 · 牛津3000 第11批",
    14: "第 14 层 · 牛津3000 第12批",
    15: "第 15 层 · 牛津3000 第13批",
    16: "第 16 层 · 牛津3000 第14批",
    17: "第 17 层 · 牛津3000 第15批",
    18: "第 18 层 · 牛津3000 第16批",
    19: "第 19 层 · 牛津3000 第17批",
    20: "第 20 层 · 牛津3000 第18批",
}


def formal_layers() -> list[tuple[int, Path]]:
    out = []
    for i in range(1, 40):
        p = ROOT / "layers" / f"layer{i}.md"
        if p.exists():
            out.append((i, p))
    return out


def render_any_layer(n: int, path: Path) -> str:
    title = LAYER_TITLES.get(n, f"第 {n} 层 · 牛津3000 批次")
    return render_entries_page(
        path, title,
        "本页正文与词条只使用第 0 层和本层前面已定义的词。打开“自测模式”先想再看。",
        "本层词条：{total} 个，全部只用前面层已定义词")


def render_index() -> str:
    core = layer0_core_count()
    tp = sum(len(s["entries"]) for s in parse_layer_file(PREVIEW_MD))
    links = ["""
<a class="biglink" href="layer0.html">
  <div class="t">第 0 层 · 基础词表</div>
  <div class="d">{core} 个公理词——直接记忆，不定义</div>
</a>""".format(core=core)]
    for n, p in formal_layers():
        cnt = sum(len(s["entries"]) for s in parse_layer_file(p))
        title = LAYER_TITLES.get(n, f"第 {n} 层 · 牛津3000 批次")
        links.append(
            f'<a class="biglink" href="layer{n}.html">'
            f'<div class="t">{title}</div>'
            f'<div class="d">{cnt} 个词条，全部只用前面层已定义词</div></a>')
    links.append(f"""
<a class="biglink" href="layer1_preview.html">
  <div class="t">第 1 层预热 · 机制演示</div>
  <div class="d">{tp} 个新词，全部只用第 0 层 {core} 词定义和举例</div>
</a>""")

    content = "".join(links) + """
<section>
  <h2>这套材料怎么读</h2>
  <ol>
    <li>先通读第 0 层词表。大部分词你早就认识，这一步是把它们正式“封存”为公理；中文速记只在这一层出现。</li>
    <li>按顺序读各层：先看每节的正文规则，再看词条；开“自测模式”可以把释义藏起来，自己先想。</li>
    <li>以后每完成一层：在 md 里写词条 → 运行 <code>python tools/build_read.py</code> 重新生成阅读版 → 运行 <code>python tools/check.py --preview</code> 验证用词不超纲。</li>
  </ol>
</section>
<section>
  <h2>三条硬规则</h2>
  <ul>
    <li>从第 1 层起，每个新词只用“第 0 层 + 之前已定义词”的英语来解释。</li>
    <li>每个词条三句话：“apple” is a noun. / The meaning of “apple” is “…”. / Example: “…”。</li>
    <li>词形变化不算新词（went→go、books→book）；禁止 don't 这类缩合形式。</li>
  </ul>
</section>
<section>
  <h2>文件与工具</h2>
  <ul>
    <li>数据源（唯一事实）：<code>layers/layer0.md</code> 到 <code>layers/layerN.md</code>（自动发现）</li>
    <li>阅读版生成：<code>python tools/build_read.py</code></li>
    <li>严格检查：<code>python tools/check.py --preview</code></li>
  </ul>
</section>
"""
    return page("English Bootstrap · 英语自举",
                f"从 {core} 个公理词出发，只用英语定义一切",
                "", "", content)


def main() -> int:
    READ.mkdir(exist_ok=True)
    files = {"read/index.html": render_index(),
             "read/layer0.html": render_layer0(),
             "read/layer1_preview.html": render_preview()}
    for n, p in formal_layers():
        files[f"read/layer{n}.html"] = render_any_layer(n, p)
    for rel, text in files.items():
        path = ROOT / rel
        path.write_text(text, encoding="utf-8")
        print(f"生成 {rel}（{len(text)} 字符）")
    print("阅读版生成完毕：打开 read/index.html 开始阅读。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
