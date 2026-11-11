"""Shared filtering for the junior textbook word list."""
import json
import re
from pathlib import Path


def key(word):
    # A trailing period is punctuation, except in abbreviations such as P.E.
    return re.sub(r"[^a-z]", "", word.lower())


def junior_words(items, primary):
    ref = json.loads((Path(__file__).parent / "level2-reference.json").read_text(encoding="utf-8"))
    basic = set(ref["words"])
    for forms in ref["forms"].values():
        basic.update(forms)
    for group in ("numbers", "ordinals", "months", "weekdays"):
        basic.update(ref[group])
    excluded = {key(w) for w in basic} | {key(item[0]) for item in primary}
    seen, result = set(), []
    for word, ipa, meaning in items:
        if "..." in word:
            continue  # Phrases belong in the phrase library, not the word library.
        if re.search(r"（[男女]名）|（姓）", meaning):
            continue
        # Source transcription errors and incorrect glosses.
        if word == "sliver":
            word, ipa, meaning = "silver", "ˈsɪlvər", "银；银色的"
        if word == "percent":
            meaning = "百分之……"
        if word.endswith(".") and word.count(".") == 1 and word.lower() not in {"mr.", "mrs.", "ms."}:
            word = word[:-1]
        k = key(word)
        if not k or k in excluded or k in seen:
            continue
        seen.add(k)
        result.append((word, ipa, meaning))
    return result
