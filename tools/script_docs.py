#!/usr/bin/env python3
"""Writes the script as readable Markdown to docs/script/ (docs/systems/faces.md):
every conversation, line by line, with each speaker's mood and tells; each
answer with what it does to trust, Suspicion and the story's flags; each
claim with its truth and what every stance costs or gains; each chapter's
scripted lines and gate visitors; and a page per person.

Generated from the game's own files: run it again after editing a script.
  tools/script_docs.py
"""
import glob
import os
import re
from collections import OrderedDict, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs/script")
CHAPTERS = ["night0", "day1", "night1", "night2", "night3", "night4", "night5", "night6"]

# The reading table (game/talk/reading.gd).
RIGHT = {"true": "believe", "hiding": "press", "lie": "confront"}
TRUST = {"true": {"believe": 2, "press": -2, "confront": -10},
         "hiding": {"believe": 0, "press": 1, "confront": -5},
         "lie": {"believe": 0, "press": 0, "confront": 0}}
CULT_SUSPICION = 10


def read(path):
    return open(os.path.join(ROOT, path), encoding="utf-8").read()


def gd_dict(src, name):
    """The entries of a GDScript `const NAME := { &"key": value, ... }`."""
    m = re.search(r"const %s := \{(.*?)\n\}" % name, src, re.S)
    return m.group(1) if m else ""


FACES = read("game/people/faces.gd")
PEOPLE = read("game/story/people.gd")
NAMES = dict(re.findall(r'&"([a-z_]+)": "([^"]+)"', gd_dict(PEOPLE, "NAMES")))
START_TRUST = {k: int(v) for k, v in re.findall(r'&"([a-z_]+)": (-?\d+)', gd_dict(PEOPLE, "START_TRUST"))}
CULT = re.findall(r'&"([a-z_]+)"', re.search(r"const CULT[^=]*=\s*\[[^\]]+\]", FACES).group(0))
BASELINES = {}
for who, body in re.findall(r'&"([a-z_]+)": \{([^}]*)\}', gd_dict(FACES, "BASELINES")):
    b = {}
    for k, v in re.findall(r'"([a-z]+)": ([^,]+)', body):
        b[k] = v.strip().strip('&"')
    BASELINES[who] = b
ALIASES = dict(re.findall(r'&"([a-z]+)": &"([a-z_]+)"', gd_dict(FACES, "ALIASES")))
CLUES = dict(re.findall(r'^\s*&"([a-z0-9_]+)": "([^"]*)"', read("game/story/clues.gd"), re.M))
MOODS = re.findall(r'&"([a-z ]+)"', re.search(r"const MOODS[^=]*=\s*\[[^\]]+\]", FACES).group(0))
TELLS = re.findall(r'&"([a-z ]+)"', re.search(r"const TELLS[^=]*=\s*\[[^\]]+\]", FACES).group(0))


def key_of(name):
    words = name.strip().lower().split()
    if not words:
        return ""
    return ALIASES.get(words[-1], words[-1])


def display(who):
    if who == "brother":
        return "A choir brother"
    return NAMES.get(who, who.replace("_", " ").title())


def chapter_titles():
    out = {}
    src = read("game/core/flow/chapters.tres")
    for block in src.split("[sub_resource")[1:]:
        cid = re.search(r'id = &"([a-z0-9]+)"', block)
        if not cid:
            continue
        heading = re.search(r'heading = "([^"]*)"', block)
        title = re.search(r'title = "([^"]*)"', block)
        out[cid.group(1)] = (heading.group(1) if heading else "", title.group(1) if title else "")
    return out


# --- Parsing a conversation -------------------------------------------------

SPOKEN = re.compile(r"^([A-Z][A-Za-z ]*?)\s*(\{([^}]*)\})?\s*:\s(.*)$")


def split_face(face):
    if not face:
        return "", []
    words = [w.strip() for w in face.split(",") if w.strip()]
    return (words[0] if words else ""), words[1:]


def tags_of(s):
    return re.findall(r"\[([^\]]*)\]", s), re.sub(r"\[[^\]]*\]", "", s).strip()


def parse_conversation(text):
    points = OrderedDict()
    cur = None
    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            if cur is None:
                points.setdefault("#notes", []).append(line.lstrip("# ").strip())
            continue
        if line.startswith("=="):
            tags, name = tags_of(line[2:])
            cur = {"name": name, "tags": tags, "lines": [], "answers": [], "jumps": []}
            points[name] = cur
            continue
        if cur is None:
            continue
        if line.startswith("*"):
            body = line[1:].strip()
            to = ""
            if "->" in body:
                body, to = body.rsplit("->", 1)
            tags, words = tags_of(body)
            cur["answers"].append({"text": words, "to": to.strip(), "tags": tags})
        elif line.startswith("->"):
            tags, to = tags_of(line[2:])
            cur["jumps"].append({"to": to, "tags": tags})
        else:
            m = SPOKEN.match(line)
            if m and "(" not in m.group(1):
                mood, tells = split_face(m.group(3))
                cur["lines"].append({"who": m.group(1).strip(), "mood": mood, "tells": tells, "text": m.group(4)})
            else:
                cur["lines"].append({"who": "", "mood": "", "tells": [], "text": line})
    return points


def conversation_text(path):
    src = read(path)
    m = re.search(r'text = "(.*)"\s*$', src, re.S)
    return m.group(1).replace('\\"', '"') if m else ""


# --- Describing tags ---------------------------------------------------------

def conditions(tags):
    out = []
    for t in tags:
        w = t.split()
        if w[0] != "if":
            continue
        neg = len(w) >= 3 and w[1] == "not"
        cond = w[-1]
        if w[-2] == "trust":
            out.append("trust %s %s" % ("below" if neg else "at least", cond))
        elif cond.startswith("night="):
            out.append("night %s" % cond.split("=")[1])
        elif cond in CLUES:
            out.append("%shas the note *%s*" % ("never " if neg else "", cond))
        else:
            out.append("%s`%s`" % ("not " if neg else "", cond))
    return out


def effects(tags):
    out = []
    for t in tags:
        w = t.split()
        if w[0] == "set":
            out.append("sets `%s`" % w[1])
        elif w[0] == "suspicion":
            out.append("**Suspicion +%s**" % w[1])
        elif w[0] == "trust":
            n = int(w[2])
            out.append("**trust %s %+d**" % (display(w[1]), n))
        elif w[0] == "note":
            out.append("writes the note *%s*" % w[1])
        elif w[0] == "item":
            out.append("gives `%s`" % w[1])
        elif w[0] in ("warn", "follow", "wait", "drink"):
            out.append({"warn": "**warns them**", "follow": "they follow him", "wait": "they wait",
                        "drink": "he drinks an ale"}[w[0]])
    return out


def stance_of(tags):
    for t in tags:
        w = t.split()
        if w[0] in ("believe", "press", "confront"):
            return w[0], (w[1] if len(w) > 1 else "")
    return "", ""


def claim_of(tags):
    for t in tags:
        w = t.split()
        if w[0] == "claim" and len(w) == 3:
            return w[1], w[2]
    return None


def read_outcome(truth, stance, who):
    right = RIGHT.get(truth) == stance
    bits = ["**right**" if right else "wrong"]
    n = TRUST.get(truth, {}).get(stance, 0)
    if n:
        bits.append("trust %+d" % n)
    if stance == "confront" and truth != "lie":
        bits.append("they remember it (`wronged_%s`)" % who)
    if stance == "confront" and truth == "lie" and who in CULT:
        bits.append("**Suspicion +%d**: the cult knows he knows" % CULT_SUSPICION)
    return ", ".join(bits)


# --- Writing a conversation --------------------------------------------------

def face_text(mood, tells):
    if not mood:
        return "*(no face)*"
    return "*%s*" % ", ".join([mood] + tells)


def write_conversation(path, who, chapter, stats):
    points = parse_conversation(conversation_text(path))
    notes = points.pop("#notes", [])
    rel = os.path.relpath(os.path.join(ROOT, path), OUT)
    md = []
    title = display(who)
    md.append("## %s\n" % title)
    md.append("[`%s`](%s)" % (os.path.basename(path), rel.replace(" ", "%20")))
    b = BASELINES.get(who)
    facts = []
    if b:
        facts.append("baseline *%s*%s" % (b.get("mood", ""), (", habit *%s*" % b["habit"]) if "habit" in b else ""))
    if who in START_TRUST:
        facts.append("starts at trust %d" % START_TRUST[who])
    if who in CULT:
        facts.append("**in the cult**")
    if facts:
        md[-1] += " · " + " · ".join(facts)
    md.append("")
    for n in notes:
        if n and n != "DRAFT":
            md.append("> %s" % n)
    if notes:
        md.append("")
    moods = []
    for name, p in points.items():
        claim = claim_of(p["tags"])
        head = "### `%s`" % name
        conds = conditions(p["tags"])
        effs = effects(p["tags"])
        if name == "again":
            head += " (the next time)"
        elif name == "leave":
            head += " (if he walks away)"
        md.append(head)
        extra = []
        if conds:
            extra.append("only if " + ", ".join(conds))
        if effs:
            extra.append(", ".join(effs))
        if extra:
            md.append("*" + "; ".join(extra) + "*")
        md.append("")
        for l in p["lines"]:
            if l["who"]:
                md.append("- **%s** %s: %s" % (l["who"], face_text(l["mood"], l["tells"]), l["text"]))
                if l["mood"]:
                    moods.append(l["mood"])
                    stats["moods"][key_of(l["who"])][chapter].append(l["mood"])
                if l["tells"]:
                    stats["tells"][key_of(l["who"])] += len(l["tells"])
            else:
                md.append("- *%s*" % l["text"].strip("()"))
        if claim:
            cid, truth = claim
            md.append("")
            md.append("> **Claim `%s`: %s.** The last line is the claim." % (cid, {"true": "true", "hiding": "true, but holding back", "lie": "a lie"}.get(truth, truth)))
            stats["claims"].append({"chapter": chapter, "who": who, "id": cid, "truth": truth,
                                    "line": p["lines"][-1]["text"] if p["lines"] else "", "file": path})
        if p["answers"] or p["jumps"]:
            md.append("")
        for i, a in enumerate(p["answers"]):
            stance, proof = stance_of(a["tags"])
            bits = []
            if stance:
                bits.append("**%s**%s" % (stance, (" with *%s*" % proof) if proof else ""))
            conds = conditions(a["tags"])
            if conds:
                bits.append("only if " + ", ".join(conds))
            effs = effects(a["tags"])
            bits += effs
            if stance and claim:
                bits.append(read_outcome(claim[1], stance, who))
            for t in a["tags"]:
                w = t.split()
                if w[0] == "trust":
                    stats["trust"][w[1]].append((chapter, who, a["text"], int(w[2])))
                if w[0] == "suspicion":
                    stats["suspicion"].append((chapter, who, a["text"], int(w[1])))
            to = a["to"] or "end"
            md.append("%d. %s → `%s`%s" % (i + 1, a["text"], to, (" · " + " · ".join(bits)) if bits else ""))
        for j in p["jumps"]:
            conds = conditions(j["tags"])
            md.append("- → `%s`%s" % (j["to"], (" if " + ", ".join(conds)) if conds else ""))
        md.append("")
    arc = " → ".join(_runs(moods)) if moods else "(no faces yet)"
    md.insert(2, "\nMoods through the talk: %s\n" % arc)
    return "\n".join(md)


def _tidy(text):
    """No more than one blank line in a row, and one newline at the end."""
    return re.sub(r"\n{3,}", "\n\n", text).rstrip() + "\n"


def _runs(seq):
    out = []
    for m in seq:
        if not out or out[-1] != m:
            out.append(m)
    return out


# --- Scenes and visitors -----------------------------------------------------

def scene_lines(chapter):
    out = []
    for path in sorted(glob.glob(os.path.join(ROOT, "game/chapters/%s/*.tscn" % chapter))):
        src = open(path, encoding="utf-8").read()
        node = ""
        for raw in src.split("\n"):
            m = re.match(r'\[node name="([^"]+)"', raw)
            if m:
                node = m.group(1)
            for s in re.findall(r'"((?:[^"\\]|\\.)*)"', raw):
                sm = SPOKEN.match(s)
                if sm and "(" not in sm.group(1) and raw.split("=")[0].strip() not in ("editor_description", "text", "duty", "title", "heading", "card"):
                    mood, tells = split_face(sm.group(3))
                    out.append((node, sm.group(1).strip(), mood, tells, sm.group(4)))
    return out


def visitors(chapter):
    out = []
    for path in sorted(glob.glob(os.path.join(ROOT, "game/chapters/%s/visitors/*.tres" % chapter))):
        src = open(path, encoding="utf-8").read()
        def field(k):
            m = re.search(r'^%s = "((?:[^"\\]|\\.)*)"' % k, src, re.M)
            return m.group(1).replace('\\"', '"') if m else ""
        answers = re.search(r'^answer = PackedStringArray\((.*)\)', src, re.M)
        out.append({"file": path, "speaker": field("speaker"), "greeting": field("greeting"),
                    "greeting_face": field("greeting_face"), "question": field("question"),
                    "answer": re.findall(r'"((?:[^"\\]|\\.)*)"', answers.group(1)) if answers else [],
                    "answer_face": field("answer_face")})
    return out


# --- Main --------------------------------------------------------------------

def main():
    os.makedirs(OUT, exist_ok=True)
    titles = chapter_titles()
    stats = {"moods": defaultdict(lambda: defaultdict(list)), "tells": defaultdict(int), "claims": [],
             "trust": defaultdict(list), "suspicion": []}
    files = []
    groups = [(c, sorted(glob.glob(os.path.join(ROOT, "game/chapters/%s/dialogue/*.tres" % c)))) for c in CHAPTERS]
    groups.append(("lane", sorted(glob.glob(os.path.join(ROOT, "game/chapters/common/lane/*.tres")))))
    for chapter, paths in groups:
        heading, title = titles.get(chapter, ("Every dusk", "The lane"))
        md = ["# %s: %s" % (heading.capitalize() if heading else chapter, title), ""]
        md.append("Generated by `tools/script_docs.py` from the game's files. Don't edit it by hand. How to read it: [README](README.md).")
        md.append("")
        if chapter == "lane":
            md.append("The lane's people at every dusk, nights 1 to 6, one talk each with a branch for each night.\n")
        for p in paths:
            who = os.path.basename(p)[:-5]
            md.append(write_conversation(os.path.relpath(p, ROOT), who, chapter, stats))
        if chapter != "lane":
            lines = scene_lines(chapter)
            if lines:
                md.append("## Scripted lines\n")
                md.append("Said by the night's beats and cues (`%s.tscn`), outside any talk.\n" % chapter)
                for node, who, mood, tells, text in lines:
                    md.append("- `%s`: **%s** %s: %s" % (node, who, face_text(mood, tells), text))
                    if mood:
                        stats["moods"][key_of(who)][chapter].append(mood)
                md.append("")
            vis = visitors(chapter)
            if vis:
                md.append("## At the gate\n")
                for v in vis:
                    md.append("- **%s** %s: %s" % (v["speaker"], face_text(*split_face(v["greeting_face"])), v["greeting"]))
                    if v["question"]:
                        md.append("  - Alric may ask: %s" % v["question"])
                        for a in v["answer"]:
                            md.append("  - **%s** %s: %s" % (v["speaker"], face_text(*split_face(v["answer_face"])), a))
                md.append("")
        name = "%s.md" % chapter
        open(os.path.join(OUT, name), "w", encoding="utf-8").write(_tidy("\n".join(md)))
        files.append((chapter, heading, title, name, len(paths)))
    write_index(files, stats)
    print("wrote %d files to docs/script/" % (len(files) + 1))


def write_index(files, stats):
    md = ["# The script", ""]
    md.append("Every conversation in the game, line by line, with each speaker's face and what each answer does to trust, Suspicion and the story. Generated by `tools/script_docs.py` from the game's own files, so it is always what the game plays. Run it again after editing a script. How faces and reading people work: `docs/systems/faces.md`.")
    md.append("")
    md.append("## Chapters\n")
    for chapter, heading, title, name, n in files:
        label = "%s: %s" % (heading.capitalize(), title) if heading else title
        md.append("- [%s](%s) (%d conversations)" % (label, name, n))
    md.append("")
    md.append("## How to read a conversation\n")
    md.append("- `### point`: a point in the talk. A talk starts at the first point, or at `again` the next time; `leave` is said if he walks away.")
    md.append("- **Name** *mood, tells*: a line, with the face it's said with. The mood is held for the line; tells play once.")
    md.append("- *Italics*: narration, what Alric sees or does.")
    md.append("- `1.` an answer Alric can give, then where it leads, its stance if it answers a claim, the conditions for it to be offered, and its effects (trust, Suspicion, flags, notes).")
    md.append("- `-` → a jump with no answer, with its condition.")
    md.append("- **Claim**: the point's last line is a claim to weigh. Each stance answer shows whether it's the right read and what it costs or gains.")
    md.append("")
    md.append("## Reading people\n")
    md.append("| The claim is | Believe | Press | Confront (with proof) |")
    md.append("| --- | --- | --- | --- |")
    md.append("| true | **right**, trust +2 | wrong, trust −2, they close up | wrong, trust −10, they remember |")
    md.append("| hiding | wrong: he never hears the rest | **right**, trust +1, they tell the rest | too hard, trust −5, they close up |")
    md.append("| a lie | wrong: he never hears the truth | half: they dig in and close up | **right**: the truth; the cult: Suspicion +10 |")
    md.append("")
    md.append("Moods: %s. Tells: %s." % (", ".join("*%s*" % m for m in MOODS), ", ".join("*%s*" % t for t in TELLS)))
    md.append("")
    md.append("## Every claim\n")
    if stats["claims"]:
        md.append("| Chapter | Who | Claim | Truth | Says |")
        md.append("| --- | --- | --- | --- | --- |")
        for c in stats["claims"]:
            md.append("| [%s](%s.md) | %s | `%s` | %s | %s |" % (c["chapter"], c["chapter"], display(c["who"]), c["id"], c["truth"], c["line"].replace("|", "/")))
    else:
        md.append("None yet.")
    md.append("")
    md.append("## Trust and Suspicion in answers\n")
    md.append("Changes written into answers (reads change trust too; see the table above).\n")
    if stats["suspicion"]:
        md.append("**Suspicion**\n")
        for chapter, who, text, n in stats["suspicion"]:
            md.append("- [%s](%s.md), %s: \"%s\" **+%d**" % (chapter, chapter, display(who), text, n))
        md.append("")
    if stats["trust"]:
        md.append("**Trust**\n")
        for target in sorted(stats["trust"]):
            for chapter, who, text, n in stats["trust"][target]:
                md.append("- %s %+d: [%s](%s.md), \"%s\"" % (display(target), n, chapter, chapter, text))
        md.append("")
    md.append("## People\n")
    people = sorted(set(list(stats["moods"].keys()) + list(BASELINES.keys())), key=lambda w: display(w))
    for who in people:
        if not who:
            continue
        b = BASELINES.get(who, {})
        line = "### %s\n" % display(who)
        md.append(line)
        facts = []
        if b:
            facts.append("Baseline *%s*" % b.get("mood", ""))
            if "habit" in b:
                facts.append("habit *%s* (means nothing from them)" % b["habit"])
            if b.get("blind") == "true":
                facts.append("blind: read the mouth and throat")
        if who in START_TRUST:
            facts.append("starts at trust %d" % START_TRUST[who])
        if who in CULT:
            facts.append("**in the cult**")
        if facts:
            text = ". ".join(facts)
            md.append(text[0].upper() + text[1:] + ".\n")
        arc = []
        for chapter in CHAPTERS + ["lane"]:
            m = stats["moods"][who].get(chapter)
            if m:
                common = max(set(m), key=m.count)
                arc.append("%s *%s*" % (chapter, common))
        if arc:
            md.append("Mostly, by chapter: " + " · ".join(arc) + ".\n")
        claims = [c for c in stats["claims"] if c["who"] == who]
        for c in claims:
            md.append("- Claim [`%s`](%s.md) (%s): \"%s\"" % (c["id"], c["chapter"], c["truth"], c["line"]))
        if claims:
            md.append("")
    open(os.path.join(OUT, "README.md"), "w", encoding="utf-8").write(_tidy("\n".join(md)))


if __name__ == "__main__":
    main()
