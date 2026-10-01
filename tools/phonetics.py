#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CMUdict(ARPAbet) → IPA 音标。缓存到 work/cmudict_ipa.json。"""
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = Path(os.environ.get("BOOTSTRAP_WORK", str(ROOT.parent.parent / "work")))
CACHE = WORK / "cmudict_ipa_v4.json"
SRC = WORK / "cmudict.dict"
IPA_DICT = WORK / "ipa_en.txt"

SYM = {
    "AA": "ɑ", "AE": "æ", "AH": "ʌ", "AO": "ɔ", "AW": "aʊ", "AY": "aɪ",
    "EH": "ɛ", "ER": "ɝ", "EY": "eɪ", "IH": "ɪ", "IY": "i", "OW": "oʊ",
    "OY": "ɔɪ", "UH": "ʊ", "UW": "u",
    "B": "b", "CH": "tʃ", "D": "d", "DH": "ð", "F": "f", "G": "ɡ",
    "HH": "h", "JH": "dʒ", "K": "k", "L": "l", "M": "m", "N": "n",
    "NG": "ŋ", "P": "p", "R": "ɹ", "S": "s", "SH": "ʃ", "T": "t",
    "TH": "θ", "V": "v", "W": "w", "Y": "j", "Z": "z", "ZH": "ʒ",
}
VOWEL_SYMS = set("ɑæʌɔaɪeɛɝɪioʊʊuəɚ")
UNSTRESSED = {"AH": "ə", "ER": "ɚ"}


def phones_to_ipa(phones):
    out = []
    last_vowel = -1
    for tok in phones:
        m = re.fullmatch(r"([A-Z]+)(\d?)", tok)
        if not m:
            continue
        base, stress = m.group(1), m.group(2)
        if base in SYM:
            sym = SYM[base]
            if stress == "0" and base in UNSTRESSED:
                sym = UNSTRESSED[base]
            if stress in ("1", "2"):
                pos = 0 if last_vowel < 0 else last_vowel + 1
                if last_vowel >= 0:
                    while pos < len(out) and out[pos] not in VOWEL_SYMS:
                        pos += 1
                out.insert(pos, "ˈ" if stress == "1" else "ˌ")
                last_vowel = pos
            out.append(sym)
            if base in SYM and sym in VOWEL_SYMS:
                last_vowel = len(out) - 1
    return "".join(out)


def load():
    newest = max((p.stat().st_mtime for p in (SRC, IPA_DICT) if p.exists()), default=0)
    if CACHE.exists() and CACHE.stat().st_mtime >= newest:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    table = {}
    if not SRC.exists():
        return table
    for line in SRC.read_text(encoding="latin-1").splitlines():
        if line.startswith(";;;") or not line.strip():
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        w = parts[0].lower()
        if "(" in w:
            continue
        if w in table:
            continue
        ipa = phones_to_ipa(parts[1:])
        if ipa:
            table[w] = ipa
    if IPA_DICT.exists():
        for line in IPA_DICT.read_text(encoding="utf-8").splitlines():
            if "\t" not in line:
                continue
            w, val = line.split("\t", 1)
            w = w.strip().lower()
            val = val.strip()
            if val.startswith("/") and val.endswith("/"):
                val = val[1:-1]
            val = val.split(",")[0].strip()
            if w and val and w not in table:
                table[w] = val
    CACHE.write_text(json.dumps(table, ensure_ascii=False, separators=(",", ":")),
                     encoding="utf-8")
    return table


def ipa_for(word: str, table: dict) -> str:
    """单词直接查；词组/连字符词用组成词拼接（空格分隔，连字符不加空）。"""
    p = table.get(word)
    if p:
        return p
    parts = re.split(r"[ -]", word)
    if len(parts) < 2:
        return ""
    got = [table.get(x, "") for x in parts]
    if any(not g for g in got):
        return ""
    return " ".join(got)


if __name__ == "__main__":
    t = load()
    print(len(t), "words")
    for w in ("apple", "ass", "as", "teacher", "beautiful"):
        print(w, t.get(w))
