#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
English Bootstrap 层检查器
==========================

用法（在 english-bootstrap/ 目录下）:
    python tools/check.py                # 检查第0层 + 所有正式层
    python tools/check.py --preview      # 额外检查 layer1_preview.md（机制演示）
    python tools/check.py --with-optional  # 第0层计入可选口语词附录

文件约定
--------
第0层    layers/layer0.md
         词表格式: 表格 | 词 | 词性 | 中文速记 |

正式层   layers/layer1.md, layers/layer2.md, ...
         每个新词一个条目，用自然语言三句话解释:
             "apple" is a noun.
             The meaning of "apple" is "..." .
             Example: "..."
         词条可以是多词（如 "present perfect"、"even though"）。
         模板句（The meaning of ... is / Example:）是固定语法关键字，
         只有引号里的定义和例句接受词汇检查。

检查规则
--------
1. 定义/例句中每个词都必须能归并到“允许词表”
   （第0层 + 之前层已定义词；常见词形变化自动归并）。
2. 缩合形式（don't 等）禁止。
3. 定义中不得出现被定义词本身（自我定义）；例句中允许。
4. 第1层起必须有词性，且词性 ∈ 已定义词性集合。
5. 层文件的正文也会被扫描（# 标题、``` 代码块、> 引用、- 条目行除外），
   保证“描述语法的句子”本身也不超纲。
6. 词尾记号 s/es/ed/ing/er/est 视为语法元符号，不算新词。
7. 释义永远只用“已定义词”；但第 4 层起（牛津三千词批次）的例句允许使用
   tools/oxford3000.txt 中列出的牛津三千词（例句不再要求逐个已自举）。

注意
----
本工具只检查“用词是否超纲”，不检查语义是否正确。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
OXFORD_FILE = ROOT / "tools" / "oxford3000.txt"
EXAMPLE_FREE_FROM_LAYER = 24  # 第 24 层起：例句不再限制用词（定义仍严格自举）

# 语法元符号：s/es/ed/ing/er/est 是词尾记号，不是英语单词
META_SYMBOLS = {"s", "es", "ed", "ing", "er", "est"}

VALID_POS = {
    "noun", "verb", "adjective", "adverb", "preposition", "conjunction",
    "pronoun", "determiner", "article", "interjection", "modal", "auxiliary",
    "number",
}

IRREGULAR = {
    # be
    "am": "be", "is": "be", "are": "be", "was": "be", "were": "be",
    "been": "be", "being": "be",
    # have
    "has": "have", "had": "have", "having": "have",
    # do
    "does": "do", "did": "do", "done": "do", "doing": "do",
    # can
    "cannot": "can",
    # say
    "says": "say", "said": "say", "saying": "say",
    # tell
    "tells": "tell", "told": "tell", "telling": "tell",
    # ask
    "asks": "ask", "asked": "ask", "asking": "ask",
    # think
    "thinks": "think", "thought": "think", "thinking": "think",
    # know
    "knows": "know", "knew": "know", "known": "know", "knowing": "know",
    # want
    "wants": "want", "wanted": "want", "wanting": "want",
    # feel
    "feels": "feel", "felt": "feel", "feeling": "feel",
    # see
    "sees": "see", "saw": "see", "seen": "see", "seeing": "see",
    # hear
    "hears": "hear", "heard": "hear", "hearing": "hear",
    # mean
    "means": "mean", "meant": "mean", "meaning": "mean",
    # happen
    "happens": "happen", "happened": "happen", "happening": "happen",
    # need
    "needs": "need", "needed": "need", "needing": "need",
    # go
    "goes": "go", "went": "go", "gone": "go", "going": "go",
    # come
    "comes": "come", "came": "come", "coming": "come",
    # move
    "moves": "move", "moved": "move", "moving": "move",
    # make
    "makes": "make", "made": "make", "making": "make",
    # give
    "gives": "give", "gave": "give", "given": "give", "giving": "give",
    # get
    "gets": "get", "got": "get", "getting": "get",
    # take
    "takes": "take", "took": "take", "taken": "take", "taking": "take",
    # use
    "uses": "use", "used": "use", "using": "use",
    # touch
    "touches": "touch", "touched": "touch", "touching": "touch",
    # open
    "opens": "open", "opened": "open", "opening": "open",
    # close
    "closes": "close", "closed": "close", "closing": "close",
    # break
    "breaks": "break", "broke": "break", "broken": "break", "breaking": "break",
    # find
    "finds": "find", "found": "find", "finding": "find",
    # hold
    "holds": "hold", "held": "hold", "holding": "hold",
    # keep
    "keeps": "keep", "kept": "keep", "keeping": "keep",
    # write
    "writes": "write", "wrote": "write", "written": "write", "writing": "write",
    # draw
    "draws": "draw", "drew": "draw", "drawn": "draw", "drawing": "draw",
    # start
    "starts": "start", "started": "start", "starting": "start",
    # stop
    "stops": "stop", "stopped": "stop", "stopping": "stop",
    # live
    "lives": "live", "lived": "live", "living": "live",
    # die
    "dies": "die", "died": "die", "dying": "die",
    # eat
    "eats": "eat", "ate": "eat", "eaten": "eat", "eating": "eat",
    # drink
    "drinks": "drink", "drank": "drink", "drunk": "drink", "drinking": "drink",
    # sleep
    "sleeps": "sleep", "slept": "sleep", "sleeping": "sleep",
    # work
    "works": "work", "worked": "work", "working": "work",
    # play
    "plays": "play", "played": "play", "playing": "play",
    # pay
    "pays": "pay", "paid": "pay", "paying": "pay",
    # stand
    "stands": "stand", "stood": "stand", "standing": "stand",
    # sit
    "sits": "sit", "sat": "sit", "sitting": "sit",
    # person / man / woman / child
    "persons": "person",
    "men": "man", "women": "woman", "children": "child", "feet": "foot",
    "teeth": "tooth",
    # 代词形式（由第1层语法处理，不算新词）
    "me": "i", "my": "i", "mine": "i", "myself": "i",
    "you": "you", "your": "you", "yours": "you",
    "yourself": "you", "yourselves": "you",
    "him": "he", "his": "he", "himself": "he",
    "her": "she", "hers": "she", "herself": "she",
    "its": "it", "itself": "it",
    "us": "we", "our": "we", "ours": "we", "ourselves": "we",
    "them": "they", "their": "they", "theirs": "they", "themselves": "they",
    # 比较级/最高级
    "better": "good", "best": "good",
    "worse": "bad", "worst": "bad",
    "bigger": "big", "biggest": "big",
    "smaller": "small", "smallest": "small",
    "longer": "long", "longest": "long",
    "shorter": "short", "shortest": "short",
    "higher": "high", "highest": "high",
    "lower": "low", "lowest": "low",
    "newer": "new", "newest": "new",
    "older": "old", "oldest": "old",
    "hotter": "hot", "hottest": "hot",
    "colder": "cold", "coldest": "cold",
    "harder": "hard", "hardest": "hard",
    "nearer": "near", "nearest": "near",
    "closer": "close", "closest": "close",
    "farther": "far", "farthest": "far", "further": "far", "furthest": "far",
}


def regular_stems(word: str) -> list[str]:
    """常见规则词形变化候选。"""
    out: list[str] = []
    if word.endswith("ies") and len(word) > 4:
        out.append(word[:-3] + "y")
    if word.endswith("es"):
        out.append(word[:-2])
        out.append(word[:-1])
    if word.endswith("s") and len(word) > 3:
        out.append(word[:-1])
    if word.endswith("ing"):
        stem = word[:-3]
        out += [stem, stem + "e"]
        if len(stem) > 2 and stem[-1] == stem[-2]:
            out.append(stem[:-1])
    if word.endswith("ed"):
        stem = word[:-2]
        out += [stem, stem + "e"]
        if len(stem) > 2 and stem[-1] == stem[-2]:
            out.append(stem[:-1])
    if word.endswith("ied"):
        out.append(word[:-3] + "y")
    if word.endswith("er") and len(word) > 3:
        out.append(word[:-2])
    if word.endswith("est") and len(word) > 4:
        out.append(word[:-3])
    if word.endswith("ly") and len(word) > 4:
        stem = word[:-2]
        out.append(stem)
        if stem.endswith("i"):
            out.append(stem[:-1] + "y")
    return out


def resolve(token: str, allowed: set[str]) -> str:
    """把词形归并到允许词表；归并不了返回空串。"""
    t = token.lower()
    if t in allowed:
        return t
    if t in IRREGULAR and IRREGULAR[t] in allowed:
        return IRREGULAR[t]
    if t.endswith("'s") and t[:-2] in allowed:
        return t[:-2]
    for cand in regular_stems(t):
        if cand in allowed:
            return cand
    return ""


TOKEN_RE = re.compile(r"[a-z]+(?:'[a-z]+)?")


def tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text.replace("’", "'").lower())


def load_layer0(with_optional: bool) -> tuple[dict[str, tuple[str, str]], list[str]]:
    """解析 layer0.md 的词汇表。返回 {词: (词性, 小节)} 与问题列表。"""
    path = ROOT / "layers" / "layer0.md"
    words: dict[str, tuple[str, str]] = {}
    problems: list[str] = []
    section = ""
    optional = False
    in_word_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            optional = "可选" in section
            in_word_table = False
            continue
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        if cells[0] == "词" and cells[1] == "词性":
            in_word_table = True
            continue
        if not in_word_table:
            continue
        w, pos = cells[0].lower(), cells[1].lower()
        if not re.fullmatch(r"[a-z]+", w):
            continue
        if optional and not with_optional:
            continue
        if w in words:
            problems.append(f"重复词: {w}（{section}）")
        if pos not in VALID_POS:
            problems.append(f"词性不合法: {w} -> {pos}（{section}）")
        words[w] = (pos, section)
    return words, problems


ENTRY_START_RE = re.compile(r'^"([a-z]+(?:\s+[a-z]+)*)"\s+is\s+(?:a|an)\s+([a-z-]+)\.$')
MEANING_RE = re.compile(r'^The meaning of "([a-z]+(?:\s+[a-z]+)*)" is "(.+)"\.$')
EXAMPLE_RE = re.compile(r'^Example:\s*"(.+)"$')


def parse_entries(path: Path) -> list[dict]:
    entries: list[dict] = []
    cur: dict | None = None
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        s = line.strip()
        m = ENTRY_START_RE.match(s)
        if m:
            if cur is not None:
                entries.append(cur)
            cur = {"word": m.group(1), "line": lineno,
                   "pos": m.group(2).lower(),
                   "defs": [], "exs": []}
            continue
        if cur is None:
            continue
        mm = MEANING_RE.match(s)
        if mm and mm.group(1) == cur["word"]:
            cur["defs"].append(mm.group(2))
            continue
        me = EXAMPLE_RE.match(s)
        if me:
            cur["exs"].append(me.group(1))
            continue
        # 其他行（小节标题、说明文字等）不属于词条
    if cur is not None:
        entries.append(cur)
    return entries


def scan_prose(path: Path) -> list[tuple[int, str]]:
    """收集层文件中需要做词汇检查的正文行。"""
    out: list[tuple[int, str]] = []
    in_fence = False
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        s = line.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not s:
            continue
        if s.startswith(("#", ">", "- ")):
            continue
        if ENTRY_START_RE.match(s) or MEANING_RE.match(s) or EXAMPLE_RE.match(s):
            continue
        out.append((lineno, s))
    return out


def check_text(text: str, allowed: set[str], phrases: set[str],
               label: str, problems: list[str]) -> bool:
    """检查一段文本的用词；有问题则记录并返回 True。"""
    t = text
    for ph in sorted(phrases, key=len, reverse=True):
        t = re.sub(r"(?<![a-z])" + re.escape(ph) + r"(?![a-z])",
                   " ", t, flags=re.IGNORECASE)
    bad: list[str] = []
    for tok in tokens(t):
        if tok in META_SYMBOLS:
            continue
        if not resolve(tok, allowed):
            bad.append(tok)
    if bad:
        shown = sorted(set(bad))
        hint = ""
        if any("'" in b for b in shown):
            hint = "（禁止缩合形式，请用完整形式）"
        problems.append(f"{label}: 出现未允许词 {shown}{hint} -> {text}")
        return True
    return False


def load_oxford() -> set[str]:
    out: set[str] = set()
    for f in (OXFORD_FILE, ROOT / "tools" / "targets.txt"):
        if f.exists():
            out |= {ln.strip().lower() for ln in f.read_text(encoding="utf-8").splitlines()
                    if ln.strip() and not ln.startswith("#")}
    return out


def validate_entry(e: dict, layer_label: str, allowed: set[str],
                   phrases: set[str], problems: list[str],
                   ex_extra: set[str] | None = None,
                   examples_free: bool = False) -> bool:
    """校验一个词条；通过则加入允许表并返回 True。"""
    ex_extra = ex_extra or set()
    w = e["word"]
    is_phrase = " " in w
    if (is_phrase and w in phrases) or (not is_phrase and w in allowed):
        problems.append(f"{layer_label} {w}（第{e['line']}行）: 该词已在允许词表中，不应重复定义")
        return False
    bad = False
    if not e["pos"]:
        problems.append(f"{layer_label} {w}（第{e['line']}行）: 缺少词性（pos）")
        bad = True
    elif e["pos"] not in VALID_POS:
        problems.append(f"{layer_label} {w}（第{e['line']}行）: 词性 '{e['pos']}' 不在已定义词性集合中")
        bad = True
    if not e["defs"]:
        problems.append(f"{layer_label} {w}（第{e['line']}行）: 缺少定义（def）")
        bad = True
    if not e["exs"]:
        problems.append(f"{layer_label} {w}（第{e['line']}行）: 缺少例句（ex）")
        bad = True
    for d in e["defs"]:
        if (is_phrase and w in d.lower()) or (not is_phrase and w in tokens(d)):
            problems.append(f"{layer_label} {w}（第{e['line']}行）: 定义中出现了被定义词本身")
            bad = True
        if check_text(d, allowed, phrases, f"{layer_label} {w} def", problems):
            bad = True
    if not examples_free:
        # 例句允许出现被定义词本身（及其词形变化）
        allowed_in_ex = allowed | ex_extra | ({w} if not is_phrase else set())
        phrases_in_ex = phrases | ({w} if is_phrase else set())
        for x in e["exs"]:
            if check_text(x, allowed_in_ex, phrases_in_ex, f"{layer_label} {w} ex", problems):
                bad = True
    if not bad:
        if is_phrase:
            phrases.add(w)
        else:
            allowed.add(w)
    return not bad


def check_entries(entries: list[dict], layer_label: str, allowed: set[str],
                  phrases: set[str], problems: list[str]) -> int:
    """按文件顺序检查所有词条。返回通过（并加入允许表）的词数。"""
    ok = 0
    for e in entries:
        if validate_entry(e, layer_label, allowed, phrases, problems):
            ok += 1
    return ok


def check_layer_sequential(path: Path, layer_label: str, allowed: set[str],
                           phrases: set[str], problems: list[str],
                           layer_no: int, oxford: set[str]) -> tuple[int, int]:
    """按文件顺序逐行检查一个层：词条先定义后使用，正文也只能用已定义词。"""
    ex_extra = oxford if layer_no >= 4 else set()
    examples_free = layer_no >= EXAMPLE_FREE_FROM_LAYER
    lines = path.read_text(encoding="utf-8").splitlines()
    total = 0
    ok = 0
    i = 0
    in_fence = False
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith("```"):
            in_fence = not in_fence
            i += 1
            continue
        if in_fence or not s or s.startswith(("#", ">", "- ")):
            i += 1
            continue
        m = ENTRY_START_RE.match(s)
        if m:
            e = {"word": m.group(1), "line": i + 1,
                 "pos": m.group(2).lower(), "defs": [], "exs": []}
            total += 1
            j = i + 1
            while j < len(lines):
                t = lines[j].strip()
                mm = MEANING_RE.match(t)
                if mm and mm.group(1) == e["word"]:
                    e["defs"].append(mm.group(2))
                    j += 1
                    continue
                me = EXAMPLE_RE.match(t)
                if me:
                    e["exs"].append(me.group(1))
                    j += 1
                    continue
                break
            if validate_entry(e, layer_label, allowed, phrases, problems,
                              ex_extra, examples_free):
                ok += 1
            i = j
            continue
        if MEANING_RE.match(s) or EXAMPLE_RE.match(s):
            i += 1  # 游离的释义/例句行（正常情况下不会出现）
            continue
        check_text(s, allowed, phrases, f"{layer_label} 正文（第{i + 1}行）", problems)
        i += 1
    return total, ok


def report_layer0(words: dict[str, tuple[str, str]], problems: list[str]) -> None:
    print("========== 第 0 层 ==========")
    total = len(words)
    print(f"词数: {total}")
    by_pos: dict[str, int] = {}
    for pos, _ in words.values():
        by_pos[pos] = by_pos.get(pos, 0) + 1
    order = ["pronoun", "article", "number", "determiner", "noun", "verb",
             "adjective", "adverb", "preposition", "conjunction", "modal",
             "interjection"]
    detail = " | ".join(f"{p} {by_pos.get(p, 0)}" for p in order if by_pos.get(p))
    print(f"按词性: {detail}")
    if problems:
        print("问题:")
        for p in problems:
            print(f"  [x] {p}")
    else:
        print("问题: 无")


def main() -> int:
    ap = argparse.ArgumentParser(description="English Bootstrap 层检查器")
    ap.add_argument("--with-optional", action="store_true",
                    help="第0层计入可选口语词附录")
    ap.add_argument("--preview", action="store_true",
                    help="额外检查 layers/layer1_preview.md（机制演示）")
    args = ap.parse_args()

    exit_code = 0

    # ---------- 第 0 层 ----------
    words, l0_problems = load_layer0(args.with_optional)
    report_layer0(words, l0_problems)
    if l0_problems:
        exit_code = 1

    allowed: set[str] = set(words)
    phrases: set[str] = set()
    oxford = load_oxford()
    if oxford:
        print(f"例句扩展词表（牛津三千）：{len(oxford)} 词（第 4 层起例句可用）")

    # ---------- 正式层 ----------
    layer_files = sorted(
        (p for p in (ROOT / "layers").glob("layer*.md")
         if re.fullmatch(r"layer[1-9]\d*\.md", p.name)),
        key=lambda p: int(p.stem[5:]),
    )
    for p in layer_files:
        layer_no = int(p.stem[5:])
        print(f"========== 第 {layer_no} 层（{p.name}） ==========")
        problems: list[str] = []
        total, ok = check_layer_sequential(p, f"第{layer_no}层", allowed, phrases,
                                           problems, layer_no, oxford)
        print(f"词条: {total}，通过: {ok}")
        if problems:
            print("问题:")
            for pr in problems:
                print(f"  [x] {pr}")
            exit_code = 1
        else:
            print("问题: 无")
        print(f"累计允许词表: {len(allowed)} 词 + {len(phrases)} 词组")

    if not layer_files:
        print("========== 正式层 ==========")
        print("尚未创建 layer1.md 等正式层（下一步：设计第 1 层）。")
        print(f"当前允许词表: {len(allowed)} 词")

    # ---------- 预热演示 ----------
    if args.preview:
        preview = ROOT / "layers" / "layer1_preview.md"
        print("========== 第 1 层预热（演示） ==========")
        problems = []
        allowed_demo = set(words)
        phrases_demo: set[str] = set()
        entries = parse_entries(preview)
        ok = check_entries(entries, "预热", allowed_demo, phrases_demo, problems)
        print(f"词条: {len(entries)}，通过: {ok}")
        if problems:
            print("问题:")
            for pr in problems:
                print(f"  [x] {pr}")
            exit_code = 1
        else:
            print(f"问题: 无（{ok} 个新词全部只用第 0 层 {len(words)} 词定义）")

    if exit_code == 0:
        print("\n检查通过 ✔")
    else:
        print("\n检查未通过，请修复上述问题。")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
