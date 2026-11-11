"""Build KEYBEAT data files from Qwerty Learner dictionaries.
usage: python3 -I build_data.py <qwerty-learner dicts dir> <out dir> <pep-vocab-3-6-by-unit.csv>
"""
import csv, json, os, random, re, sys

SRC, OUT, PEPCSV = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)
OK = re.compile(r"^[A-Za-z][A-Za-z '.\-]*$")


def load(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return json.load(fh)


def clean_text(w):
    w = str(w).replace("’", "'").replace("‘", "'").replace(" ", " ")
    w = re.sub(r"\s+", " ", w).strip()
    return w


def clean_trans(t):
    if isinstance(t, list):
        t = "；".join(str(x) for x in t if x)
    t = str(t or "")
    t = re.sub(r"【.*", "", t)                 # mnemonic notes
    t = re.sub(r"<(\S{1,3})>", r"（\1）", t)       # <美> style tags
    t = t.replace("<", "").replace(">", "").replace("`", "").replace("\\", "")
    t = re.sub(r"\s+A(?=\s*[；;]|\s*$)", "", t)   # stray frequency markers
    t = re.sub(r"\s+", " ", t).replace("， ", "，").replace("； ", "；").strip(" ；;,，")
    t = re.sub(r"^phrase\.\s*", "", t)
    if len(t) > 46:
        cut = max(t.rfind("；", 0, 46), t.rfind("，", 0, 46), t.rfind(";", 0, 46))
        t = t[:cut] if cut > 12 else t[:45] + "…"
    return t.replace("\t", " ").replace("\n", " ")


def clean_ipa(p):
    p = str(p or "").strip()
    if not p or p.lower() == "none":
        return ""
    p = p.split(";")[0].strip().strip("[]/ ")
    p = p.replace("`", "ˈ").replace("\u200b", "")
    p = p.replace("'", "ˈ").replace("ˋ", "ˈ").replace(",", "ˌ").replace("\t", " ")
    return p if len(p) <= 40 else ""


def entries(names):
    out = []
    for n in names:
        for e in load(n):
            w = clean_text(e.get("name", ""))
            zh = clean_trans(e.get("trans"))
            if not w or not zh or not OK.match(w) or w.endswith("-"):
                continue
            out.append((w, clean_ipa(e.get("usphone")), zh))
    return out


def dedupe(items):
    seen, out = set(), []
    for it in items:
        k = it[0].lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(it)
    return out


def words(items, maxlen=20):
    return [it for it in items if " " not in it[0] and 2 <= len(it[0]) <= maxlen]


def phrases(items, maxlen=30):
    return [it for it in items if " " in it[0] and len(it[0]) <= maxlen]


def shuffled(items, seed):
    items = list(items)
    random.Random(seed).shuffle(items)
    return items


XX = ["PEP_SL_XiaoXue%d_%d_t.json" % (g, s) for g in (1, 2) for s in (1, 2)] + \
     ["PEPXiaoXue%d_%d_T.json" % (g, s) for g in (3, 4, 5, 6) for s in (1, 2)]
CZ = ["PEPChuZhong7_1_T.json", "PEPChuZhong7_2_T.json", "PEPChuZhong8_1_T.json", "PEPChuZhong8_2_T.json", "PEPChuZhong9_1_T.json"]
GZ = ["PEPGaoZhong_%d_T.json" % i for i in range(1, 12)]

xx, cz, gz = entries(XX), entries(CZ), entries(GZ)


# primary school, PEP grade-3 start: one volume per term, one chapter per textbook unit.
# Source: a by-unit table transcribed from the textbook appendices (volume, unit, word, phonetic, meaning).
primary, pvol_phr, seen_vu = [], [], set()
with open(PEPCSV, encoding="utf-8-sig", newline="") as fh:
    for r in csv.DictReader(fh):
        w = clean_text(re.sub(r"\(.*?\)|…", " ", r["word"]))
        zh = clean_trans(r["meaning"]).replace("(alsoEarth)", "（也作 Earth）").replace("(alsotheMoon)", "（也作 the Moon）")
        # keep weak/strong forms ("kən, kæn"); drop a transcription that covers only part of a phrase
        ipa = re.sub(r"\s*,\s*", "; ", r["phonetic"].strip().strip("[]/ ")).replace("ː l", "ːl")
        if w == "T-shirt T":
            w, zh = "T-shirt", "T恤衫"
        if w == "set thetable":
            w = "set the table"
        if " " in w and len(ipa.split()) < len(w.split()):
            ipa = ""
        vol = r["volume"].replace("上", "a").replace("下", "b")
        unit = re.sub(r"\D", "", r["unit"])
        if not w or not zh or not OK.match(w) or (vol, w.lower()) in seen_vu:
            print("skip", r["volume"], r["unit"], r["word"])
            continue
        seen_vu.add((vol, w.lower()))
        primary.append((w, ipa, zh, vol, unit))
        if " " in w:
            pvol_phr.append((w, ipa, zh))
pset = {it[0].lower() for it in primary} | {w.lower() for w, _, _ in words(xx)}
junior = [it for it in dedupe(words(cz)) if it[0].lower() not in pset]

lists = {
    "primary": primary,
    "junior": junior,
    "senior": shuffled(dedupe(words(entries(["GaoKao_3500.json"]))), 3500),
    "cet4": dedupe(words(entries(["CET4_T.json"]))),
    "cet6": dedupe(words(entries(["CET6_T.json"]))),
    "kaoyan": dedupe(words(entries(["KaoYan_3_T.json"]))),
    "toefl": dedupe(words(entries(["TOEFL_3_T.json"]))),
    "ielts": dedupe(words(entries(["IELTS_3_T.json"]))),
    "dev": dedupe(words(entries(["it-words.json"]))),
    "med": dedupe(words(entries(["BIOmedical.json"]))),
    "p1": dedupe(pvol_phr + phrases(xx)),
    "p2": dedupe(phrases(cz)),
    "p3": dedupe(phrases(gz)),
    "p4": dedupe(phrases(entries(["Common-Phrases-FCE-Unofficial.json", "Common-Phrases-PTE-Unofficial.json"]))),
    "p5": dedupe(phrases(entries(["IELTS_WANG_5.json"]))),
}
for key, items in lists.items():
    body = "\n".join("\t".join(it) for it in items)
    with open(os.path.join(OUT, key + ".js"), "w", encoding="utf-8") as fh:
        fh.write("KB_DATA(%s,%s);\n" % (json.dumps(key), json.dumps(body, ensure_ascii=False)))
    size = os.path.getsize(os.path.join(OUT, key + ".js"))
    print(key, len(items), "%dKB" % (size // 1024), "|", " / ".join(items[0]), "|", " / ".join(items[len(items) // 2]))
