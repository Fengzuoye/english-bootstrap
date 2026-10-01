#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 layer1/layer2 的语法知识点整理成 App 用 Accordion 数据（grammar.json）。

结构：topic = {id, title, layer, note(系统讲解), examples[], words[]}
words 使用 dict.json 里的词条（含音标、释义、层级），顺序保持层文件顺序。
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NOTES = {
    (1, 1): "英语句子由词组成；sentence 是能表达完整意思的一组词，form 是同一个词的不同形式（如 go / goes / went）。先认识这两个概念，后面所有语法都建立在此基础上。",
    (1, 2): "词性决定一个词在句子里做什么：noun（名词）指人/物/地点，verb（动词）表示动作或状态，adjective（形容词）描述人或物，adverb（副词）说明时间、地点、方式。还有 preposition（介词）、conjunction（连词）、pronoun（代词）、determiner（限定词）、article（冠词）、modal（情态动词）、auxiliary（助动词）与 interjection（感叹词）。判断词性是分析句子的第一步。",
    (1, 3): "英语句子有固定词序：主语（谁/什么）+ 谓语（做什么/是什么）+ 宾语/表语（对象或补充说明）。疑问句、否定句也在这个骨架上变化，所以先掌握基本词序。",
    (1, 4): "名词分可数与不可数；可数名词有单数和复数（a book / two books）。a/an 用在单数可数名词前，the 表示双方都知道的那个；不可数名词一般不加 a/an。",
    (1, 5): "代词用来代替名词，避免重复：人称代词（I/you/he/she/it/we/they）、物主代词（my/your/his/our…）、反身代词（myself/yourself…）、指示代词（this/that/these/those）。代词要和它指代的人或物在人称、数上对应。",
    (1, 6): "时间与频率词告诉动作发生在什么时候、多久一次、排第几：数字与序数词（one…first…）、时间词（today, week, year）、频率词（always, often, sometimes, never）。它们常和时态配合使用。",
    (1, 7): "时态起步：一般现在（经常发生/事实）、现在进行（正在发生）、一般过去（过去发生）、一般将来（will + 动词原形）、现在完成（已经发生并对现在有影响）。先掌握这几种就能表达大多数日常内容。",
    (1, 8): "疑问与否定靠助动词：do/does/did + 动词原形构成否定与一般疑问；疑问词（what/where/when/why/how/who）放在句首；疑问句要把助动词或 be 动词提前。词序错了，句意就会变。",
    (2, 1): "时态完备：除基础时态外，还有过去完成（had + 过去分词，表示“过去的过去”）、将来进行（will be + doing）、将来完成（will have + 过去分词）、以及完成进行（have/has/had been + doing），用来表达更精确的时间关系。",
    (2, 2): "情态动词（can/could/may/might/must/should/will/would）放在动词原形前，表达能力、可能、义务、建议或意愿；情态动词不随人称变化，否定直接加 not。",
    (2, 3): "被动语态用 be + 过去分词，强调动作的承受者而不是执行者：The book was written by him。不同时态只需改变 be 的形式。",
    (2, 4): "比较用来对比两个或多个人或物：比较级 + than（more/…er）、最高级（the most/…est）、as … as（和……一样）。注意不规则形式 good/better/best。",
    (2, 5): "从句是把一个完整句子当作另一个句子的一部分：定语从句（who/which/that）、宾语从句（that/if/whether）、状语从句（when/because/if/although）。从句要有自己的主语和谓语。",
    (2, 6): "条件句表示“如果……就……”：真实条件用 if + 一般现在，主句用 will；虚拟条件用 if + 过去式，主句用 would + 动词原形，表示与事实相反。",
    (2, 7): "间接引语转述别人的话：时态往过去推一步，人称和时间状语随之调整（now→then, today→that day），并常用 say/tell + that 引导。",
    (2, 8): "非谓语动词不做谓语：不定式（to do）常表目的或将来，动名词（doing）相当于名词，分词（doing/done）作定语或状语。一个句子只能有一个谓语，其余动作用非谓语。",
    (2, 9): "疑问补充：反意疑问句（You are ready, aren't you?）用简短问句确认信息；附加疑问要与前半句的人称、时态和肯定/否定相反。",
    (2, 10): "there be 表示“某处有某物”，be 与后面的名词一致；it 可作形式主语或指时间、天气、距离（It is cold / It is five o'clock）。",
    (2, 11): "连接词把词、短语或句子连起来：and/or/but 连接并列成分，because/so 表因果，although 表让步，if/when 表条件或时间，that 引导从句。",
}


def parse_layer(path: Path, layer_no: int):
    topics = []
    cur = None
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("## "):
            title = re.sub(r"^\d+\.\s*", "", s[3:].strip())
            cur = {"title": title, "layer": layer_no, "words": [], "examples": []}
            topics.append(cur)
            continue
        if cur is None:
            continue
        m = re.match(r'^"([^"]+)"\s+is\s+(?:a|an)\s+[a-z-]+\.$', s)
        if m:
            cur["words"].append(m.group(1))
            continue
        m = re.match(r'^Example:\s*"(.+)"$', s)
        if m:
            cur["examples"].append(m.group(1))
    return topics


def main():
    dict_path = ROOT / "android" / "english-bootstrap-app" / "app" / "src" / "main" / "assets" / "dict.json"
    words = json.loads(dict_path.read_text(encoding="utf-8"))["words"]
    by_word = {}
    for e in words:
        by_word.setdefault(e["w"], e)

    out = []
    for layer_no in (1, 2):
        for i, t in enumerate(parse_layer(ROOT / "layers" / f"layer{layer_no}.md", layer_no)):
            tid = f"g{layer_no}-{i+1}"
            cards = []
            for w in t["words"]:
                e = by_word.get(w)
                if e:
                    cards.append({k: e.get(k) for k in ("w", "pos", "def", "ex", "p", "l", "zh")})
            exs = []
            for x in t["examples"]:
                if x not in exs:
                    exs.append(x)
            out.append({
                "id": tid, "title": t["title"], "layer": layer_no,
                "note": NOTES.get((layer_no, i + 1), ""),
                "examples": exs[:6], "words": cards,
            })

    dest = ROOT / "android" / "english-bootstrap-app" / "app" / "src" / "main" / "assets" / "grammar.json"
    dest.write_text(json.dumps({"topics": out}, ensure_ascii=False, separators=(",", ":")),
                    encoding="utf-8")
    print(f"语法知识点 {len(out)} 个，词卡 {sum(len(t['words']) for t in out)} 张 -> {dest}")


if __name__ == "__main__":
    main()
