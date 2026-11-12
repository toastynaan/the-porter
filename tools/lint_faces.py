#!/usr/bin/env python3
"""Checks faces, claims and stances in conversations and scene lines
(docs/systems/faces.md) without starting Godot, the same rules the game's
parser uses (game/talk/conversation.gd, game/people/faces.gd). Also lists
spoken lines that have no face yet.

  tools/lint_faces.py                     every conversation and chapter scene
  tools/lint_faces.py game/chapters/night3  only under that folder
  tools/lint_faces.py --quiet ...          errors only, no missing-face list
Exits 1 if any file has an error.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _consts():
    faces = open(os.path.join(ROOT, "game/people/faces.gd")).read()
    moods = re.findall(r'&"([a-z ]+)"', re.search(r"const MOODS[^=]*=\s*\[[^\]]+\]", faces).group(0))
    tells = re.findall(r'&"([a-z ]+)"', re.search(r"const TELLS[^=]*=\s*\[[^\]]+\]", faces).group(0))
    clues = re.findall(r'^\s*&"([a-z0-9_]+)":', open(os.path.join(ROOT, "game/story/clues.gd")).read(), re.M)
    return set(moods), set(tells), set(clues)


MOODS, TELLS, CLUES = _consts()
TRUTHS = {"true", "hiding", "lie", "mistaken", "misleading"}
SPOKEN = re.compile(r"^([A-Z][A-Za-z ]*?)\s*(\{[^}]*\})?\s*:\s")


def face_errors(face):
    out = []
    words = [w.strip().lower() for w in face.strip("{}").split(",") if w.strip()]
    if not words:
        return ["empty {}"]
    if words[0] not in MOODS:
        out.append("unknown mood {%s}" % words[0])
    for t in words[1:]:
        if t not in TELLS:
            out.append("unknown tell {%s}" % t)
    return out


def tag_list(s):
    return re.findall(r"\[([^\]]*)\]", s)


def lint_conversation(path, text, first=1):
    """`first`: the file's line number of the text's first line."""
    errors, missing = [], []
    points, current = {}, None
    for n, raw in enumerate(text.split("\n"), first):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("=="):
            head = line[2:].strip()
            name = re.sub(r"\[[^\]]*\]", "", head).strip()
            current = {"name": name, "tags": tag_list(head), "lines": [], "answers": [], "jumps": []}
            if name in points:
                errors.append("%d: a second point called %s" % (n, name))
            points[name] = current
            for t in current["tags"]:
                w = t.split()
                if w[0] == "claim" and (len(w) != 3 or w[2] not in TRUTHS):
                    errors.append("%d: bad claim [%s] (claim <id> true|hiding|lie|mistaken|misleading)" % (n, t))
            continue
        if current is None:
            errors.append("%d: a line before any point" % n)
            continue
        if line.startswith("*"):
            body = line[1:].strip()
            to = body.rsplit("->", 1)[1].strip() if "->" in body else None
            if to is None:
                errors.append("%d: an answer with no ->" % n)
            tags = tag_list(body)
            for t in tags:
                w = t.split()
                if w[0] == "confront" and (len(w) != 2 or w[1] not in CLUES):
                    errors.append("%d: [confront %s] names no clue in game/story/clues.gd" % (n, " ".join(w[1:])))
            current["answers"].append({"to": to, "tags": tags, "n": n})
            continue
        if line.startswith("->"):
            current["jumps"].append(re.sub(r"\[[^\]]*\]", "", line[2:]).strip())
            continue
        m = SPOKEN.match(line)
        if m and "(" not in m.group(1):
            if m.group(2):
                for e in face_errors(m.group(2)):
                    errors.append("%d: %s" % (n, e))
            else:
                missing.append(n)
            current["lines"].append(("speaker", n))
        else:
            current["lines"].append(("narration", n))
    for p in points.values():
        stances = [a for a in p["answers"] if any(t.split()[0] in ("believe", "press", "confront") for t in a["tags"])]
        claim = [t for t in p["tags"] if t.split()[0] == "claim"]
        if len(p["answers"]) > 3:
            errors.append("%s: %d answers (three at most)" % (p["name"], len(p["answers"])))
        if p["answers"] and p["jumps"]:
            errors.append("%s: both answers and ->" % p["name"])
        if stances and not claim:
            errors.append("%s: a stance on a point with no [claim]" % p["name"])
        if claim and (not p["lines"] or p["lines"][-1][0] != "speaker"):
            errors.append("%s: a [claim] whose last line nobody says" % p["name"])
        for to in [a["to"] for a in p["answers"] if a["to"]] + p["jumps"]:
            if to != "end" and to not in points:
                errors.append("%s: no point called %s" % (p["name"], to))
    return errors, missing


# Scene properties whose strings are labels, not speech ("Dusk: the road into London").
NOT_SPEECH = ("duty", "editor_description", "title", "heading", "card", "text")


def lint_scene(path, text):
    errors, missing = [], []
    for m in re.finditer(r'"([A-Z][A-Za-z]+(?: [A-Z][a-z]+)?)\s*(\{[^}]*\})?: [^"]+"', text):
        n = text.count("\n", 0, m.start()) + 1
        key = text[text.rfind("\n", 0, m.start()) + 1:m.start()].split("=")[0].strip()
        if key in NOT_SPEECH:
            continue
        if m.group(2):
            for e in face_errors(m.group(2)):
                errors.append("%d: %s" % (n, e))
        else:
            missing.append(n)
    return errors, missing


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    quiet = "--quiet" in sys.argv
    roots = args or ["game/chapters"]
    files = []
    for r in roots:
        r = os.path.join(ROOT, r)
        files += glob.glob(os.path.join(r, "**/*.tres"), recursive=True) + glob.glob(os.path.join(r, "**/*.tscn"), recursive=True)
    bad = False
    total_missing = 0
    for f in sorted(set(files)):
        text = open(f, encoding="utf-8").read()
        rel = os.path.relpath(f, ROOT)
        if 'script_class="Conversation"' in text:
            m = re.search(r'text = "(.*)"\s*$', text, re.S)
            body = m.group(1).replace('\\"', '"') if m else ""
            first = text.count("\n", 0, m.start(1)) + 1 if m else 1
            errors, missing = lint_conversation(rel, body, first)
            # A bare " inside the text ends Godot's string there: the rest is lost.
            if m:
                bare = re.search(r'(?<!\\)"', m.group(1))
                if bare:
                    n = text.count("\n", 0, m.start(1) + bare.start()) + 1
                    errors.append("%d: a \" inside the text must be written \\\"" % n)
        elif f.endswith(".tscn"):
            errors, missing = lint_scene(rel, text)
        else:
            continue
        for e in errors:
            print("ERROR %s: %s" % (rel, e))
            bad = True
        total_missing += len(missing)
        if missing and not quiet:
            print("no face %s: lines %s" % (rel, ", ".join(map(str, missing[:12])) + (" ..." if len(missing) > 12 else "")))
    print("%s; %d spoken lines with no face" % ("errors" if bad else "ok", total_missing))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
