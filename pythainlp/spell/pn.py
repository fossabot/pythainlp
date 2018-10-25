# -*- coding: utf-8 -*-
"""
Spell checker, using Peter Norvig algorithm + word frequency from Thai National Corpus

Based on Peter Norvig's Python code from http://norvig.com/spell-correct.html
"""
from collections import Counter

from pythainlp.corpus import tnc
from pythainlp.util import is_thaichar


def _keep(word):
    for ch in word:
        if ch != "." and not is_thaichar(ch):
            return False
        if ch in "๐๑๒๓๔๕๖๗๘๙":
            return False
    return True


# get word frequency from TNC then filter out non-Thai words and low frequency words
word_freqs = tnc.get_word_frequency_all()
word_freqs = [
    word_freq
    for word_freq in word_freqs
    if word_freq[1] > 2 and len(word_freq[0]) <= 40 and _keep(word_freq[0])
]

_WORDS = Counter(dict(word_freqs))
_WORDS_TOTAL = sum(_WORDS.values())


def _prob(word, n=_WORDS_TOTAL):
    "Probability of `word`."
    return _WORDS[word] / n


def _known(words):
    return list(w for w in words if w in _WORDS)


def _edits1(word):
    letters = [
        "ก",
        "ข",
        "ฃ",
        "ค",
        "ฅ",
        "ฆ",
        "ง",
        "จ",
        "ฉ",
        "ช",
        "ซ",
        "ฌ",
        "ญ",
        "ฎ",
        "ฏ",
        "ฐ",
        "ฑ",
        "ฒ",
        "ณ",
        "ด",
        "ต",
        "ถ",
        "ท",
        "ธ",
        "น",
        "บ",
        "ป",
        "ผ",
        "ฝ",
        "พ",
        "ฟ",
        "ภ",
        "ม",
        "ย",
        "ร",
        "ฤ",
        "ล",
        "ฦ",
        "ว",
        "ศ",
        "ษ",
        "ส",
        "ห",
        "ฬ",
        "อ",
        "ฮ",
        "ฯ",
        "ะ",
        "ั",
        "า",
        "ำ",
        "ิ",
        "ี",
        "ึ",
        "ื",
        "ุ",
        "ู",
        "ฺ",
        "\u0e3b",
        "\u0e3c",
        "\u0e3d",
        "\u0e3e",
        "฿",
        "เ",
        "แ",
        "โ",
        "ใ",
        "ไ",
        "ๅ",
        "ๆ",
        "็",
        "่",
        "้",
        "๊",
        "๋",
        "์",
    ]
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]

    return set(deletes + transposes + replaces + inserts)


def _edits2(word):
    return (e2 for e1 in _edits1(word) for e2 in _edits1(e1))


def spell(word):
    """
    Return a list of possible words, according to edit distance
    """
    if not word:
        return ""

    return _known([word]) or _known(_edits1(word)) or _known(_edits2(word)) or [word]


def correction(word):
    """
    Return the most possible word, according to probability from the corpus
    แสดงคำที่เป็นไปได้มากที่สุด
    """
    return max(spell(word), key=_prob)
