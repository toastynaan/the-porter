#!/usr/bin/env python3
"""Writes the game's script to docs/script/, from the game's own files
(tools/script_model.py reads them):

- one page per chapter: the night's map (a sequence diagram: its beats in
  order, who he can talk to when, and the flags that pass between them),
  then every conversation as a flowchart of all its paths, with its lines,
  faces, claims and what each answer does;
- links.md: every flag and note, who sets it and who reads it;
- README.md: how to read it all, every claim, every trust and Suspicion
  change, and a page per person;
- script.json: the same, as data, for the interactive page.

The diagrams are Mermaid: GitHub, VS Code and Obsidian draw them.
Run it again after editing a script:
  tools/script_docs.py
"""
import json
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import script_model as M  # noqa: E402

OUT = os.path.join(M.ROOT, "docs/script")


# --- Words -----------------------------------------------------------------------

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
        elif cond in M.CLUES:
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
            out.append("**trust %s %+d**" % (M.display(w[1]), int(w[2])))
        elif w[0] == "note":
            out.append("writes the note *%s*" % w[1])
        elif w[0] == "item":
            out.append("gives `%s`" % w[1])
        elif w[0] in ("warn", "follow", "wait", "drink"):
            out.append({"warn": "**warns them**", "follow": "they follow him", "wait": "they wait",
                        "drink": "he drinks an ale"}[w[0]])
    return out


def read_outcome(truth, stance, who):
    right = stance in M.RIGHT.get(truth, [])
    bits = ["**right**" if right else "wrong"]
    n = M.TRUST.get(truth, {}).get(stance, 0)
    if n:
        bits.append("trust %+d" % n)
    if stance == "confront" and truth in ("true", "hiding"):
        bits.append("they remember it (`wronged_%s`)" % who)
    if stance == "confront" and truth in ("lie", "misleading") and who in M.CULT:
        bits.append("**Suspicion +%d**: the cult knows he knows" % M.CULT_SUSPICION)
    return ", ".join(bits)


def face_text(mood, tells):
    return "*%s*" % ", ".join([mood] + tells) if mood else "*(no face)*"


def runs(seq):
    out = []
    for m in seq:
        if not out or out[-1] != m:
            out.append(m)
    return out


def tidy(text):
    return re.sub(r"\n{3,}", "\n\n", text).rstrip() + "\n"


def mm(text, limit=60):
    """Text safe inside a Mermaid label in quotes."""
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return text.replace('"', "'").replace("<", "‹").replace(">", "›").replace("#", "no.").replace(";", ",").replace("|", "/")


def node_id(name):
    return "p_" + re.sub(r"[^A-Za-z0-9_]", "_", name)


# --- One conversation's flowchart ----------------------------------------------------

STANCE_COLOUR = {True: "#3f7d4c", False: "#a8433a"}


def flowchart(talk):
    lines = ["```mermaid", "flowchart TD"]
    styles = []
    edges = 0
    used = set()
    for name, p in talk.points.items():
        label = ["<b>%s</b>" % mm(name, 40)]
        first = next((l for l in p["lines"] if l["who"]), None)
        if first:
            label.append("%s: %s" % (mm(first["who"], 20), mm(first["text"], 54)))
        elif p["lines"]:
            label.append("<i>%s</i>" % mm(p["lines"][0]["text"].strip("()"), 54))
        effs = [e.replace("**", "").replace("`", "").replace("*", "") for e in effects(p["tags"])]
        if effs:
            label.append("<i>%s</i>" % mm(", ".join(effs), 60))
        claim = M.claim_of(p["tags"])
        if claim:
            label.append("⚖ claim: %s" % claim[1])
        shape = ("{{", "}}") if claim else ("[", "]")
        lines.append('  %s%s"%s"%s' % (node_id(name), shape[0], "<br/>".join(label), shape[1]))
        if claim:
            styles.append("  class %s claim" % node_id(name))
        if name in ("again",) or name.startswith("again_"):
            styles.append("  class %s again" % node_id(name))
        if name == "leave":
            styles.append("  class %s leave" % node_id(name))
        used.add(name)
    lines.append('  end_((end))')
    for name, p in talk.points.items():
        claim = M.claim_of(p["tags"])
        for a in p["answers"]:
            stance, proof = M.stance_of(a["tags"])
            bits = [mm(a["text"], 38)]
            if stance:
                bits.insert(0, "[%s%s]" % (stance, (" " + proof) if proof else ""))
            conds = [c.replace("`", "").replace("*", "") for c in conditions(a["tags"])]
            if conds:
                bits.append("if " + mm(", ".join(conds), 40))
            to = a["to"] if a["to"] in talk.points else "end_" if a["to"] == "end" else a["to"]
            lines.append('  %s -->|"%s"| %s' % (node_id(name), "<br/>".join(bits), node_id(to) if to != "end_" else "end_"))
            if stance and claim:
                right = stance in M.RIGHT.get(claim[1], [])
                styles.append("  linkStyle %d stroke:%s,stroke-width:2px" % (edges, STANCE_COLOUR[right]))
            edges += 1
        for j in p["jumps"]:
            conds = [c.replace("`", "").replace("*", "") for c in conditions(j["tags"])]
            to = j["to"] if j["to"] in talk.points else "end_"
            label = ' -.->|"if %s"| ' % mm(", ".join(conds), 40) if conds else " -.-> "
            lines.append("  %s%s%s" % (node_id(name), label, node_id(to) if to != "end_" else "end_"))
            edges += 1
    lines.append("  classDef claim fill:#f3e3b5,stroke:#9a6b1a,color:#2b2116")
    lines.append("  classDef again fill:#e3e8ef,stroke:#5b6b80,color:#1c2430")
    lines.append("  classDef leave fill:#eee,stroke:#999,color:#333,stroke-dasharray: 3 3")
    lines += styles
    lines.append("```")
    return "\n".join(lines)


# --- One conversation's lines -----------------------------------------------------------

def talk_lines(talk, stats):
    md = []
    for name, p in talk.points.items():
        claim = M.claim_of(p["tags"])
        head = "#### `%s`" % name + (" (the next time)" if name == "again" else " (if he walks away)" if name == "leave" else "")
        md.append(head)
        extra = []
        if conditions(p["tags"]):
            extra.append("only if " + ", ".join(conditions(p["tags"])))
        if effects(p["tags"]):
            extra.append(", ".join(effects(p["tags"])))
        if extra:
            md.append("*" + "; ".join(extra) + "*")
        md.append("")
        for l in p["lines"]:
            if l["who"]:
                md.append("- **%s** %s: %s" % (l["who"], face_text(l["mood"], l["tells"]), l["text"]))
                if l["mood"]:
                    stats["moods"][M.key_of(l["who"])][talk.chapter].append(l["mood"])
            else:
                md.append("- *%s*" % l["text"].strip("()"))
        if claim:
            md.append("")
            md.append("> **Claim `%s`: %s.** The last line is the claim." % (claim[0], M.TRUTH_WORDS.get(claim[1], claim[1])))
        if p["answers"] or p["jumps"]:
            md.append("")
        for i, a in enumerate(p["answers"]):
            stance, proof = M.stance_of(a["tags"])
            bits = []
            if stance:
                bits.append("**%s**%s" % (stance, (" with *%s*" % proof) if proof else ""))
            if conditions(a["tags"]):
                bits.append("only if " + ", ".join(conditions(a["tags"])))
            bits += effects(a["tags"])
            if stance and claim:
                bits.append(read_outcome(claim[1], stance, talk.person))
            for t in a["tags"]:
                w = t.split()
                if w[0] == "trust":
                    stats["trust"][w[1]].append((talk.chapter, talk.person, a["text"], int(w[2])))
                if w[0] == "suspicion":
                    stats["suspicion"].append((talk.chapter, talk.person, a["text"], int(w[1])))
            md.append("%d. %s → `%s`%s" % (i + 1, a["text"], a["to"], (" · " + " · ".join(bits)) if bits else ""))
        for j in p["jumps"]:
            conds = conditions(j["tags"])
            md.append("- → `%s`%s" % (j["to"], (" if " + ", ".join(conds)) if conds else ""))
        md.append("")
    return "\n".join(md)


def talk_section(talk, links, stats):
    who = talk.person
    title = M.display(who) if talk.file == who else "%s (%s)" % (M.display(who), talk.file.replace("_", " "))
    md = ['<a id="%s"></a>' % anchor(talk.file), "## %s" % title, ""]
    facts = ["[`%s`](%s)" % (os.path.basename(talk.path), os.path.relpath(os.path.join(M.ROOT, talk.path), OUT)),
             "id `%s`" % talk.id]
    b = M.BASELINES.get(who)
    if b:
        facts.append("baseline *%s*%s" % (b.get("mood", ""), (", habit *%s*" % b["habit"]) if "habit" in b else ""))
    if who in M.START_TRUST:
        facts.append("starts at trust %d" % M.START_TRUST[who])
    if who in M.CULT:
        facts.append("**in the cult**")
    md.append(" · ".join(facts))
    md.append("")
    moods = [l["mood"] for p in talk.points.values() for l in p["lines"] if l["mood"]]
    if moods:
        md.append("Moods through the talk: %s" % " → ".join(runs(moods)))
        md.append("")
    for n in talk.notes:
        md.append("> %s" % n)
    md.append("")
    # What links this talk to the rest of the game.
    ins = sorted(f for f in talk.reads if f not in talk.sets)
    outs = sorted(f for f in talk.sets if any(r[1] is not talk for r in links.get(f, {}).get("read", [])))
    if ins:
        md.append("**Reads from elsewhere:** " + ", ".join("[`%s`](links.md#%s)" % (f, anchor(f)) for f in ins))
    if outs:
        md.append("**Read elsewhere:** " + ", ".join("[`%s`](links.md#%s)" % (f, anchor(f)) for f in outs))
    md.append("")
    md.append("### Every path")
    md.append("")
    md.append(flowchart(talk))
    md.append("")
    md.append("<details><summary>Every line</summary>")
    md.append("")
    md.append(talk_lines(talk, stats))
    md.append("</details>")
    md.append("")
    for c in talk.claims():
        stats["claims"].append(dict(c, chapter=talk.chapter, who=who))
    return "\n".join(md)


def anchor(name):
    return re.sub(r"[^a-z0-9_-]", "", name.lower())


# --- A night's map ----------------------------------------------------------------------

def night_map(chapter, talks_by_path, links):
    lines = ["```mermaid", "sequenceDiagram", "  autonumber"]
    lines.append("  participant A as Alric")
    lines.append("  participant N as The night")
    people = []
    alias = {}

    def who(path):
        t = talks_by_path.get(path)
        name = M.display(t.person) if t else os.path.basename(path)[:-5]
        if name not in alias:
            alias[name] = "P%d" % (len(alias) + 1)
            people.append(name)
        return alias[name], t

    body = []
    shown = set()
    chapter_talks = {p for b in chapter.beats for p in b["talks"]} | {t["talk"] for t in chapter.talkers}
    for b in chapter.beats:
        body.append('  Note over A,N: %s · %s%s' % (mm(b["name"], 20), M.PHASES[b["phase"]] if b["phase"] < len(M.PHASES) else b["phase"],
                                                  (" · " + mm(b["duty"], 44)) if b["duty"] else ""))
        for path in b["talks"]:
            if path in shown or not path.endswith(".talk"):
                continue
            shown.add(path)
            a, t = who(path)
            body.append("  N->>%s: opens %s (%s)" % (a, os.path.basename(path), mm(b.get("via", {}).get(path, ""), 30)))
            body += link_lines(a, t, chapter_talks, talks_by_path, who)
        # Who he can go and talk to from here: the first beat of their phase
        # that doesn't open talks itself.
        if not b["talks"]:
            free = [t for t in chapter.talkers if t["talk"] not in shown and b["phase"] in t["phases"]]
            lane = [t for t in free if "/common/lane/" in t["talk"]]
            for t in free:
                if t in lane:
                    continue
                shown.add(t["talk"])
                a, tk = who(t["talk"])
                body.append("  A->>%s: can talk (%s)" % (a, os.path.basename(t["talk"])))
                body += link_lines(a, tk, chapter_talks, talks_by_path, who)
            if lane:
                for t in lane:
                    shown.add(t["talk"])
                body.append("  Note right of A: The lane at dusk: %s (see the lane page)" % ", ".join(sorted({t["who"] for t in lane})))
        for f in sorted(b["sets"]):
            readers = [r for r in links.get(f, {}).get("read", []) if r[0] == "talk" and r[1].path in chapter_talks]
            for r in readers:
                a, _ = who(r[1].path)
                body.append("  N-->>%s: %s" % (a, mm(f, 40)))
    for name in people:
        lines.append("  participant %s as %s" % (alias[name], mm(name, 30)))
    lines += body
    later = carries_on(chapter, chapter_talks, talks_by_path, links)
    if later:
        lines.append("  Note over A,N: carries on: %s" % mm(", ".join(later), 140))
    lines.append("```")
    return "\n".join(lines)


def link_lines(a, talk, chapter_talks, talks_by_path, who):
    """A talk's flags that another talk of this chapter reads: a dashed arrow to it."""
    out = []
    if talk is None:
        return out
    for f in sorted(talk.sets):
        if f.startswith("talked_"):
            continue
        for path in sorted(chapter_talks):
            t2 = talks_by_path.get(path)
            if t2 is None or t2 is talk or f not in t2.reads:
                continue
            b, _ = who(path)
            label = f if b != a else "%s (to %s)" % (f, os.path.basename(path))
            out.append("  %s-->>%s: %s" % (a, b, mm(label, 60)))
    return out


def carries_on(chapter, chapter_talks, talks_by_path, links):
    """Flags set in this chapter's talks that later chapters read."""
    order = M.CHAPTERS + ["lane"]
    here = order.index(chapter.id)
    out = []
    for path in chapter_talks:
        t = talks_by_path.get(path)
        if not t or t.chapter != chapter.id:
            continue
        for f in t.sets:
            if f.startswith("talked_"):
                continue
            for r in links.get(f, {}).get("read", []):
                if r[0] == "talk" and r[1].chapter in order and order.index(r[1].chapter) > here:
                    out.append(f)
                    break
    return sorted(set(out))


# --- Chapter pages -----------------------------------------------------------------------

def chapter_page(chapter, talks, talks_by_path, links, stats):
    title = "%s: %s" % (chapter.heading.capitalize(), chapter.title) if chapter.heading else chapter.title
    md = ["# %s" % title, ""]
    md.append("Generated by `tools/script_docs.py` from the game's files. Don't edit it by hand. How to read it: [README](README.md). Every flag: [links](links.md).")
    md.append("")
    if chapter.beats:
        md.append("## The night")
        md.append("")
        md.append("The chapter's beats in order (`%s`), the talks each opens, who he can go to from then on, and the flags passed between them (dashed). The note at the end lists what this chapter's talks pass on to later ones." % os.path.basename(chapter.scene))
        md.append("")
        md.append(night_map(chapter, talks_by_path, links))
        md.append("")
    md.append("## Conversations")
    md.append("")
    for t in talks:
        md.append("- [%s](#%s) (`%s`)" % (M.display(t.person), anchor(t.file), os.path.basename(t.path)))
    md.append("")
    for t in talks:
        md.append(talk_section(t, links, stats))
    if chapter.id != "lane":
        lines = scene_lines(chapter)
        if lines:
            md.append("## Scripted lines\n")
            md.append("Said by the night's beats and cues (`%s`), outside any talk.\n" % os.path.basename(chapter.scene))
            for node, who, mood, tells, text in lines:
                md.append("- `%s`: **%s** %s: %s" % (node, who, face_text(mood, tells), text))
                if mood:
                    stats["moods"][M.key_of(who)][chapter.id].append(mood)
            md.append("")
    return tidy("\n".join(md))


def scene_lines(chapter):
    out = []
    ext, nodes = M.parse_tscn(chapter.scene)
    for n in nodes:
        for k, v in n.props.items():
            if k in ("editor_description", "text", "duty", "title", "heading", "card"):
                continue
            for s in re.findall(r'"((?:[^"\\]|\\.)*)"', v):
                sm = M.SPOKEN.match(s)
                if sm and "(" not in sm.group(1):
                    mood, tells = M.split_face(sm.group(3))
                    out.append((n.path, sm.group(1).strip(), mood, tells, sm.group(4)))
    return out


class LaneChapter:
    id = "lane"
    beats = []
    talkers = []
    heading = "Every dusk"
    title = "The lane"
    scene = "game/chapters/common/night_base.tscn"


# --- The links page ------------------------------------------------------------------------

def links_page(links):
    md = ["# Every flag and note", ""]
    md.append("Who sets each flag or note, and who reads it, across every conversation, scene and script. Generated by `tools/script_docs.py`. A flag the night's prefix builds (`GameState.tonight(\"x\")` is `n<night>_x`) or a family built at run time (`died_<who>`) is followed to where it's made.")
    md.append("")
    unset = [f for f, v in links.items() if v["read"] and not v["set"]]
    unread = [f for f, v in links.items() if v["set"] and not v["read"]]
    md.append("## Problems")
    md.append("")
    if unset:
        md.append("**Read but never set** (a condition that can never hold):")
        md.append("")
        for f in unset:
            md.append("- [`%s`](#%s)" % (f, anchor(f)))
    else:
        md.append("Every flag and note that is read is set somewhere.")
    md.append("")
    md.append("<details><summary>Set but never read (%d): bookkeeping (talked_, reads), notes that count toward the prior, or loose ends</summary>" % len(unread))
    md.append("")
    md.append(", ".join("`%s`" % f for f in unread))
    md.append("")
    md.append("</details>")
    md.append("")
    md.append("## Every flag")
    md.append("")
    for f, v in links.items():
        kind = "note" if f in M.CLUES else "flag"
        md.append('<a id="%s"></a>' % anchor(f))
        md.append("### `%s`%s" % (f, " (a note: %s)" % M.CLUES[f] if kind == "note" else ""))
        md.append("")
        md.append("- **Set by:** " + ("; ".join(M.where_text(*s) for s in v["set"]) if v["set"] else "*nothing*"))
        md.append("- **Read by:** " + ("; ".join(M.where_text(*r) for r in v["read"]) if v["read"] else "*nothing*"))
        md.append("")
    return tidy("\n".join(md))


# --- The index ----------------------------------------------------------------------------

def index_page(chapters, talks_by_chapter, stats):
    md = ["# The script", ""]
    md.append("Every conversation in the game, how they link, and what each answer does. Generated by `tools/script_docs.py` from the game's own files, so it is always what the game plays: run it again after editing a script. The script itself is in each chapter's folder (`game/chapters/<chapter>/dialogue/*.talk`, the lane's in `game/chapters/common/lane/`). Faces and reading people: `docs/systems/faces.md`. Writing a conversation: `docs/systems/dialogue.md`.")
    md.append("")
    md.append("## Chapters\n")
    for c in chapters:
        n = len(talks_by_chapter.get(c.id, []))
        label = "%s: %s" % (c.heading.capitalize(), c.title) if c.heading else c.title
        md.append("- [%s](%s.md): %d conversations%s" % (label, c.id, n, ", %d beats" % len(c.beats) if c.beats else ""))
    md.append("- [Every flag and note](links.md): who sets it, who reads it, and any that are read but never set")
    md.append("")
    md.append("## How to read it\n")
    md.append("**A night's map** (sequence diagram): the night's beats run down the page in order (`Note over Alric, The night`). Under each, a solid arrow from *The night* is a talk the beat opens itself (the traveller on the ride); a solid arrow from *Alric* is someone he can go and talk to from then on. A dashed arrow is a flag one talk sets and another reads. The last note lists what passes on to later chapters.")
    md.append("")
    md.append("**A conversation** (flowchart): every point is a box with its first line; every answer is a solid arrow labelled with what Alric says, its stance in brackets if it answers a claim, and its condition; a dotted arrow is a jump with no answer. A claim is a six-sided box; a stance arrow is green if it's the right read, red if wrong. `again` (the next time) is blue-grey; `leave` (if he walks away) is dashed. Under it, *Every line* opens the whole script with faces and effects.")
    md.append("")
    md.append("## Reading people\n")
    md.append("| The claim is | Believe | Press | Confront (with proof) |")
    md.append("| --- | --- | --- | --- |")
    md.append("| true | **right**, trust +2 | wrong, trust −2, they close up | wrong, trust −10, they remember |")
    md.append("| hiding | wrong: he never hears the rest | **right**, trust +1, they tell the rest | too hard, trust −5, they close up |")
    md.append("| a lie | wrong: he never hears the truth | half: they dig in and close up | **right**: the truth; the cult: Suspicion +10 |")
    md.append("| mistaken | wrong: he takes their error for his own | **right**, trust +1: they think again | **right**, trust +2: they're shown |")
    md.append("| misleading | wrong: he goes where they point | **right**: he isn't led | **right**; the cult: Suspicion +10 |")
    md.append("")
    md.append("Moods: %s. Tells: %s." % (", ".join("*%s*" % m for m in M.MOODS), ", ".join("*%s*" % t for t in M.TELLS)))
    md.append("")
    md.append("## Every claim\n")
    md.append("| Chapter | Who | Claim | Truth | Says |")
    md.append("| --- | --- | --- | --- | --- |")
    for c in stats["claims"]:
        md.append("| [%s](%s.md) | %s | `%s` | %s | %s |" % (c["chapter"], c["chapter"], M.display(c["who"]), c["id"], c["truth"], c["line"].replace("|", "/")))
    md.append("")
    md.append("## Trust and Suspicion in answers\n")
    md.append("Changes written into answers (reads change trust too: see the table above).\n")
    if stats["suspicion"]:
        md.append("**Suspicion**\n")
        for chapter, who, text, n in stats["suspicion"]:
            md.append("- [%s](%s.md), %s: \"%s\" **+%d**" % (chapter, chapter, M.display(who), text, n))
        md.append("")
    if stats["trust"]:
        md.append("**Trust**\n")
        for target in sorted(stats["trust"]):
            for chapter, who, text, n in stats["trust"][target]:
                md.append("- %s %+d: [%s](%s.md), \"%s\"" % (M.display(target), n, chapter, chapter, text))
        md.append("")
    md.append("## People\n")
    people = sorted({w for w in stats["moods"] if w} | set(M.BASELINES), key=M.display)
    for who in people:
        b = M.BASELINES.get(who, {})
        md.append("### %s\n" % M.display(who))
        facts = []
        if b:
            facts.append("baseline *%s*" % b.get("mood", ""))
            if "habit" in b:
                facts.append("habit *%s* (means nothing from them)" % b["habit"])
            if b.get("blind") == "true":
                facts.append("blind: read the mouth and throat")
        if who in M.START_TRUST:
            facts.append("starts at trust %d" % M.START_TRUST[who])
        if who in M.CULT:
            facts.append("**in the cult**")
        if facts:
            text = ". ".join(facts)
            md.append(text[0].upper() + text[1:] + ".\n")
        arc = []
        for chapter in M.CHAPTERS + ["lane"]:
            m = stats["moods"][who].get(chapter)
            if m:
                arc.append("%s *%s*" % (chapter, max(set(m), key=m.count)))
        if arc:
            md.append("Mostly, by chapter: " + " · ".join(arc) + ".\n")
        for c in [c for c in stats["claims"] if c["who"] == who]:
            md.append("- Claim [`%s`](%s.md) (%s): \"%s\"" % (c["id"], c["chapter"], c["truth"], c["line"]))
        md.append("")
    return tidy("\n".join(md))


# --- JSON -----------------------------------------------------------------------------------

def as_json(chapters, talks, links):
    def where(w):
        kind, owner, text = w
        return {"kind": kind, "talk": owner.path if kind == "talk" else None, "chapter": getattr(owner, "chapter", None) or getattr(owner, "id", None),
                "where": text}
    return {
        "chapters": [{"id": c.id, "title": c.title, "heading": c.heading, "night": c.night,
                      "beats": [{"name": b["name"], "phase": M.PHASES[b["phase"]] if b["phase"] < len(M.PHASES) else b["phase"],
                                 "duty": b["duty"], "talks": b["talks"], "sets": sorted(b["sets"])} for b in c.beats],
                      "talkers": c.talkers} for c in chapters],
        "talks": {t.path: {"id": t.id, "person": t.person, "name": M.display(t.person), "chapter": t.chapter, "notes": t.notes,
                           "points": [{"name": n, "tags": p["tags"], "claim": M.claim_of(p["tags"]), "lines": p["lines"],
                                       "answers": [{"text": a["text"], "to": a["to"], "tags": a["tags"],
                                                    "stance": M.stance_of(a["tags"])[0] or None,
                                                    "right": (M.stance_of(a["tags"])[0] in M.RIGHT.get((M.claim_of(p["tags"]) or ("", ""))[1], []))
                                                    if M.stance_of(a["tags"])[0] and M.claim_of(p["tags"]) else None}
                                                   for a in p["answers"]],
                                       "jumps": p["jumps"]} for n, p in t.points.items()],
                           "sets": sorted(t.sets), "reads": sorted(t.reads)} for t in talks},
        "links": {f: {"set": [where(s) for s in v["set"]], "read": [where(r) for r in v["read"]]} for f, v in links.items()},
        "people": {w: {"name": M.display(w), "baseline": M.BASELINES.get(w), "trust": M.START_TRUST.get(w), "cult": w in M.CULT}
                   for w in sorted({t.person for t in talks} | set(M.BASELINES))},
        "clues": M.CLUES,
    }


# --- Main ---------------------------------------------------------------------------------

def main():
    os.makedirs(OUT, exist_ok=True)
    talks, chapters, code, links = M.load_all()
    talks_by_path = {t.path: t for t in talks}
    by_chapter = defaultdict(list)
    for t in talks:
        by_chapter[t.chapter].append(t)
    stats = {"moods": defaultdict(lambda: defaultdict(list)), "claims": [], "trust": defaultdict(list), "suspicion": []}
    pages = chapters + [LaneChapter()]
    for c in pages:
        page = chapter_page(c, by_chapter.get(c.id, []), talks_by_path, links, stats)
        open(os.path.join(OUT, "%s.md" % c.id), "w", encoding="utf-8").write(page)
    open(os.path.join(OUT, "links.md"), "w", encoding="utf-8").write(links_page(links))
    open(os.path.join(OUT, "README.md"), "w", encoding="utf-8").write(index_page(pages, by_chapter, stats))
    with open(os.path.join(OUT, "script.json"), "w", encoding="utf-8") as f:
        json.dump(as_json(chapters, talks, links), f, indent=1, ensure_ascii=False)
    unset = [f for f, v in links.items() if v["read"] and not v["set"]]
    print("wrote %d pages, links.md and script.json to docs/script/; %d flags read but never set" % (len(pages) + 1, len(unset)))


if __name__ == "__main__":
    main()
