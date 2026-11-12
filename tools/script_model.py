"""The game's script as data, read from the game's own files (docs/systems/dialogue.md,
docs/systems/faces.md): every conversation (.talk), every chapter's beats and who
can be talked to when, and every flag and note: who sets it and who reads it.
tools/script_docs.py writes it out as Markdown and JSON.

Flags are set in five ways, and all five are followed here:
- named in a conversation's tags ([set x], [note x]) or in code (set_flag(&"x"), note(&"x"));
- through the night's prefix (GameState.tonight("x") is n<night>_x): in a
  chapter's own code and a beat's `flag` property, that night; in the
  shared routine, every night;
- by a scene property (`flag = &"x"` on a ride cue, a visitor, a body);
- by the conversation system itself (talked_<id>, read_<claim>, wronged_<who>);
- in families built at run time (died_<who>, moved_<id>, fed_<soul> ...).
"""
import glob
import os
import re
from collections import OrderedDict, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAPTERS = ["night0", "day1", "night1", "night2", "night3", "night4", "night5", "night6"]
PHASES = ["supper", "gate", "knocks", "matins", "round", "dawn", "dusk", "small hours"]


def read(path):
    return open(os.path.join(ROOT, path), encoding="utf-8").read()


def rel(path):
    return os.path.relpath(path, ROOT) if os.path.isabs(path) else path


# --- Reference data -----------------------------------------------------------

def _gd_dict(src, name):
    m = re.search(r"const %s := \{(.*?)\n\}" % name, src, re.S)
    return m.group(1) if m else ""


FACES_SRC = read("game/people/faces.gd")
PEOPLE_SRC = read("game/story/people.gd")
NAMES = dict(re.findall(r'&"([a-z_]+)": "([^"]+)"', _gd_dict(PEOPLE_SRC, "NAMES")))
START_TRUST = {k: int(v) for k, v in re.findall(r'&"([a-z_]+)": (-?\d+)', _gd_dict(PEOPLE_SRC, "START_TRUST"))}
CULT = re.findall(r'&"([a-z_]+)"', re.search(r"const CULT[^=]*=\s*\[[^\]]+\]", FACES_SRC).group(0))
MOODS = re.findall(r'&"([a-z ]+)"', re.search(r"const MOODS[^=]*=\s*\[[^\]]+\]", FACES_SRC).group(0))
TELLS = re.findall(r'&"([a-z ]+)"', re.search(r"const TELLS[^=]*=\s*\[[^\]]+\]", FACES_SRC).group(0))
ALIASES = dict(re.findall(r'&"([a-z]+)": &"([a-z_]+)"', _gd_dict(FACES_SRC, "ALIASES")))
BASELINES = {}
for _who, _body in re.findall(r'&"([a-z_]+)": \{([^}]*)\}', _gd_dict(FACES_SRC, "BASELINES")):
    BASELINES[_who] = {k: v.strip().strip('&"') for k, v in re.findall(r'"([a-z]+)": ([^,]+)', _body)}
CLUES = dict(re.findall(r'^\s*&"([a-z0-9_]+)": "([^"]*)"', read("game/story/clues.gd"), re.M))

# The reading table (game/talk/reading.gd).
RIGHT = {"true": ["believe"], "hiding": ["press"], "lie": ["confront"],
         "mistaken": ["press", "confront"], "misleading": ["press", "confront"]}
TRUST = {"true": {"believe": 2, "press": -2, "confront": -10},
         "hiding": {"believe": 0, "press": 1, "confront": -5},
         "lie": {"believe": 0, "press": 0, "confront": 0},
         "mistaken": {"believe": 0, "press": 1, "confront": 2},
         "misleading": {"believe": 0, "press": 0, "confront": 0}}
TRUTH_WORDS = {"true": "true", "hiding": "true, but holding back", "lie": "a lie",
               "mistaken": "mistaken: they believe it, and it isn't so",
               "misleading": "misleading: true words, said to lead him wrong"}
CULT_SUSPICION = 10


def key_of(name):
    words = name.strip().lower().split()
    return ALIASES.get(words[-1], words[-1]) if words else ""


def display(who):
    if who == "brother":
        return "A choir brother"
    return NAMES.get(who, who.replace("_", " ").title())


def chapter_info():
    out = {}
    src = read("game/core/flow/chapters.tres")
    for block in src.split("[sub_resource")[1:]:
        cid = re.search(r'id = &"([a-z0-9]+)"', block)
        if not cid:
            continue
        g = lambda k: (re.search(r'%s = "([^"]*)"' % k, block) or [None, ""])[1]
        night = re.search(r"^night = (\d+)", block, re.M)
        out[cid.group(1)] = {"heading": g("heading"), "title": g("title"), "night": int(night.group(1)) if night else 0}
    out.setdefault("lane", {"heading": "Every dusk", "title": "The lane", "night": None})
    return out


CHAPTER_INFO = chapter_info()


# --- Conversations ------------------------------------------------------------

SPOKEN = re.compile(r"^([A-Z][A-Za-z ]*?)\s*(\{([^}]*)\})?\s*:\s(.*)$")


def split_face(face):
    words = [w.strip() for w in (face or "").split(",") if w.strip()]
    return (words[0] if words else ""), words[1:]


def tags_of(s):
    return re.findall(r"\[([^\]]*)\]", s), re.sub(r"\[[^\]]*\]", "", s).strip()


def flag_name(cond):
    return cond.split("=")[0]


class Talk:
    """One conversation (.talk)."""

    def __init__(self, path, chapter):
        self.path = path
        self.chapter = chapter
        self.person = os.path.basename(path)[:-5]
        src = read(path)
        lines = src.split("\n")
        self.id = lines[0][4:].strip() if lines and lines[0].startswith("@id ") else self.person
        self.notes = []
        self.points = OrderedDict()
        self._parse("\n".join(lines[1:]) if lines and lines[0].startswith("@id ") else src)
        self.file = self.person
        # Who it is: the one who speaks most in it (traveller_road is the traveller).
        if self.person not in NAMES and self.person not in BASELINES:
            speakers = [key_of(l["who"]) for p in self.points.values() for l in p["lines"] if l["who"]]
            if speakers:
                self.person = max(set(speakers), key=speakers.count)
        self.sets = defaultdict(list)    # flag -> [where]
        self.reads = defaultdict(list)   # flag -> [where]
        self._links()

    def _parse(self, text):
        cur = None
        for raw in text.split("\n"):
            line = raw.strip()
            if not line:
                continue
            if line.startswith("#"):
                if cur is None and line.lstrip("# ").strip() not in ("DRAFT", ""):
                    self.notes.append(line.lstrip("# ").strip())
                continue
            if line.startswith("=="):
                tags, name = tags_of(line[2:])
                cur = {"name": name, "tags": tags, "lines": [], "answers": [], "jumps": []}
                self.points[name] = cur
            elif cur is None:
                continue
            elif line.startswith("*"):
                body, to = (line[1:].strip().rsplit("->", 1) + [""])[:2]
                tags, words = tags_of(body)
                cur["answers"].append({"text": words, "to": to.strip() or "end", "tags": tags})
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

    def _links(self):
        self.sets["talked_" + self.id].append("(any talk)")
        for name, p in self.points.items():
            self._tags(p["tags"], name)
            c = claim_of(p["tags"])
            if c:
                self.sets["read_" + c[0]].append(name)
                self.sets["read_%s_right" % c[0]].append(name)
            for a in p["answers"]:
                self._tags(a["tags"], "%s: \"%s\"" % (name, a["text"]))
                if stance_of(a["tags"])[0] == "confront" and c and c[1] in ("true", "hiding"):
                    self.sets["wronged_" + self.person].append(name)
            for j in p["jumps"]:
                self._tags(j["tags"], name)

    def _tags(self, tags, where):
        for t in tags:
            w = t.split()
            if w[0] == "set":
                self.sets[flag_name(w[1])].append(where)
            elif w[0] == "note":
                self.sets[w[1]].append(where)
            elif w[0] == "if" and w[-2] != "trust" and not w[-1].startswith("night="):
                self.reads[flag_name(w[-1])].append(where)
            elif w[0] == "confront" and len(w) == 2:
                self.reads[w[1]].append(where)

    def claims(self):
        out = []
        for name, p in self.points.items():
            c = claim_of(p["tags"])
            if c:
                out.append({"point": name, "id": c[0], "truth": c[1], "line": p["lines"][-1]["text"] if p["lines"] else ""})
        return out


def claim_of(tags):
    for t in tags:
        w = t.split()
        if w[0] == "claim" and len(w) == 3:
            return w[1], w[2]
    return None


def stance_of(tags):
    for t in tags:
        w = t.split()
        if w[0] in ("believe", "press", "confront"):
            return w[0], (w[1] if len(w) > 1 else "")
    return "", ""


def load_talks():
    talks = []
    for c in CHAPTERS:
        for p in sorted(glob.glob(os.path.join(ROOT, "game/chapters/%s/dialogue/*.talk" % c))):
            talks.append(Talk(rel(p), c))
    for p in sorted(glob.glob(os.path.join(ROOT, "game/chapters/common/lane/*.talk"))):
        talks.append(Talk(rel(p), "lane"))
    return talks


# --- Scenes: beats, talkers, and the flags they set -------------------------------

class Node:
    def __init__(self, name, parent, header):
        self.name = name
        self.parent = parent
        self.header = header
        self.props = OrderedDict()

    @property
    def path(self):
        return self.name if self.parent in (None, ".") else "%s/%s" % (self.parent, self.name)


def parse_tscn(path):
    src = read(path)
    ext = dict((m[1], m[0]) for m in re.findall(r'\[ext_resource [^\]]*path="([^"]+)"[^\]]*id="([^"]+)"\]', src))
    nodes = []
    cur = None
    for raw in src.split("\n"):
        m = re.match(r'\[node name="([^"]+)"(?:[^\]]*parent="([^"]*)")?', raw)
        if m:
            cur = Node(m.group(1), m.group(2), raw)
            nodes.append(cur)
            inst = re.search(r'instance=ExtResource\("([^"]+)"\)', raw)
            if inst:
                cur.props["instance"] = ext.get(inst.group(1), "")
            continue
        if re.match(r"\[(sub_resource|ext_resource|resource\]|connection|gd_scene|gd_resource|editable)", raw):
            cur = None
            continue
        if cur is not None and " = " in raw:
            k, v = raw.split(" = ", 1)
            cur.props[k.strip()] = v.strip()
    return ext, nodes


def _ext_paths(value, ext):
    return [ext[i] for i in re.findall(r'ExtResource\("([^"]+)"\)', value) if i in ext]


class Chapter:
    """A chapter's beats in order, who can be talked to when, and what its scene sets."""

    def __init__(self, cid):
        self.id = cid
        info = CHAPTER_INFO.get(cid, {})
        self.night = info.get("night", 0)
        self.title = info.get("title", cid)
        self.heading = info.get("heading", "")
        self.scene = "game/chapters/%s/%s.tscn" % (cid, cid)
        self.beats = []        # {name, script, phase, duty, talks: [paths], sets: {flag: where}}
        self.talkers = []      # {who, talk, phases}
        self.other_talks = []  # {node, talk}: opened by something that isn't a beat or a talker
        self.sets = defaultdict(list)
        self.reads = defaultdict(list)
        self._read()

    def _read(self):
        base_ext, base_nodes = parse_tscn("game/chapters/common/night_base.tscn")
        ext, nodes = parse_tscn(self.scene)
        inherits = "night_base.tscn" in read(self.scene).split("\n")[2] or any(n.props.get("instance", "").endswith("night_base.tscn") for n in nodes[:1])
        talkers = OrderedDict()
        if inherits:
            for n in base_nodes:
                if n.name == "Talker":
                    talkers[n.parent] = {"phases": n.props.get("phases", ""), "talk": _ext_paths(n.props.get("conversation", ""), base_ext)}
        for n in nodes:
            if n.name == "Talker":
                t = talkers.setdefault(n.parent, {"phases": "", "talk": []})
                if "phases" in n.props:
                    t["phases"] = n.props["phases"]
                if "conversation" in n.props:
                    t["talk"] = _ext_paths(n.props["conversation"], ext)
        for parent, t in talkers.items():
            if t["talk"] and t["talk"][0].endswith(".talk"):
                phases = [int(x) for x in re.findall(r"\d+", t["phases"])] or [6]
                self.talkers.append({"who": parent.split("/")[-1], "talk": t["talk"][0].replace("res://", ""), "phases": phases})
        scripts = dict(ext)
        for n in nodes:
            script = scripts.get(re.search(r'ExtResource\("([^"]+)"\)', n.props.get("script", "x")).group(1), "") if n.props.get("script") else ""
            talks = [p.replace("res://", "") for k, v in n.props.items() for p in _ext_paths(v, ext) if p.endswith(".talk")]
            via = {p.replace("res://", ""): k for k, v in n.props.items() for p in _ext_paths(v, ext) if p.endswith(".talk")}
            if n.parent == "Director":
                beat = {"name": n.name, "script": script.replace("res://", ""), "phase": int(n.props.get("phase", "0")),
                        "duty": n.props.get("duty", "").strip('"'), "talks": talks, "via": via, "refs": " ".join(n.props.values()),
                        "sets": defaultdict(list)}
                self.beats.append(beat)
            elif n.name != "Talker" and talks:
                self.other_talks.append({"node": n.path, "talks": talks, "via": {p: "%s.%s" % (n.path, k) for p, k in via.items()}})
            # Scene properties that set or read flags and notes.
            tonight = script.endswith(("lines_beat.gd", "scene_beat.gd"))
            for k, v in n.props.items():
                # Tags written into a scene's question ("set n2_told_hugh=gate; trust hugh -5").
                for s_ in re.findall(r'"([^"]*)"', v):
                    for part in s_.split(";"):
                        w = part.split()
                        if len(w) == 2 and w[0] == "set":
                            self.sets[flag_name(w[1])].append("%s (%s.tscn)" % (n.path, self.id))
                if k == "start_flags":
                    for name in re.findall(r'&"([a-z0-9_]+)"', v):
                        self.sets[name].append("assumed when %s is started on its own (%s.tscn)" % (self.id, self.id))
                    continue
                for name in re.findall(r'&"([a-z0-9_]+)"', v):
                    where = "%s (%s.tscn)" % (n.path, self.id)
                    if k in ("flag", "found_flag", "seen_flag") or k.endswith("_flag"):
                        f = "n%d_%s" % (self.night, name) if tonight else name
                        self.sets[f].append(where)
                        if n.parent == "Director":
                            self.beats[-1]["sets"][f].append(where)
                    elif k in ("note", "clue") or (name in CLUES and "note" in k):
                        self.sets[name].append(where)
                    elif k in ("only_if", "needs", "if_flag"):
                        self.reads[name].append(where)
        # Talks opened by something outside the director (the ride's cues) belong
        # to the beat that holds that thing.
        for o in self.other_talks:
            top = o["node"].split("/")[0]
            owner = next((b for b in self.beats if ('"../../%s"' % top) in b["refs"] or ('../../%s")' % top) in b["refs"]), None)
            if owner:
                for t in o["talks"]:
                    if t not in owner["talks"]:
                        owner["talks"].append(t)
                        owner["via"][t] = o["via"][t]


def load_chapters():
    return [Chapter(c) for c in CHAPTERS]


# --- Code: flags set and read by scripts -------------------------------------------

class Code:
    def __init__(self):
        self.sets = defaultdict(list)
        self.reads = defaultdict(list)
        self.families = defaultdict(set)    # prefix -> files
        self.suffixes = defaultdict(set)    # suffix -> files: <visitor flag>_fate
        self.tonight_families = defaultdict(set)  # prefix -> files: n<night>_warned_<who>
        self.tonight_all = defaultdict(list)  # x -> files (shared code: n<any night>_x)
        for path in sorted(glob.glob(os.path.join(ROOT, "game/**/*.gd"), recursive=True)):
            r = rel(path)
            if "/tests/" in r:
                continue
            src = open(path, encoding="utf-8").read()
            chapter = re.match(r"game/chapters/([a-z0-9]+)/", r)
            night = CHAPTER_INFO.get(chapter.group(1), {}).get("night") if chapter and chapter.group(1) != "common" else None
            for x in re.findall(r'set_flag\(&"([a-z0-9_]+)"', src):
                self.sets[x].append(r)
            for call in re.findall(r'\bnote\(([^()\n]*)\)', src):
                for x in re.findall(r'&"([a-z0-9_]+)"', call):
                    self.sets[x].append(r)
            for x in re.findall(r'set_flag\(GameState\.tonight\("([a-z0-9_]+)"\)', src) + re.findall(r'set_flag\(tonight\("([a-z0-9_]+)"\)', src):
                if night is not None:
                    self.sets["n%d_%s" % (night, x)].append(r)
                else:
                    self.tonight_all[x].append(r)
            # A flag an exported property names by default (warned_flag := &"bread_warned").
            for x in re.findall(r'@export var \w*flag\w* := &"([a-z0-9_]+)"', src):
                self.sets[x].append(r)
            for x in re.findall(r'\+\s*"(_[a-z_]+)"\)', src):
                self.suffixes[x].add(r)
            for x in re.findall(r'tonight\("([a-z_]+_)"\s*\+', src):
                self.tonight_families[x].add(r)
            for x in re.findall(r'(?:has_flag|get_flag|has_note)\(&"([a-z0-9_]+)"', src):
                self.reads[x].append(r)
            for x in re.findall(r'(?:has_flag|get_flag)\(GameState\.tonight\("([a-z0-9_]+)"\)', src):
                self.reads[("n%d_%s" % (night, x)) if night is not None else ("n*_" + x)].append(r)
            for p in re.findall(r'StringName\("([a-z_]+_)"\s*\+', src) + re.findall(r'"([a-z_]+_)%s"', src):
                self.families[p].add(r)
            if 'StringName("night%d_done"' in src:
                self.families["night"].add(r)


# --- Links ----------------------------------------------------------------------------

def build_links(talks, chapters, code):
    """Every flag and note: [{name, set: [(kind, where)], read: [(kind, where)]}]."""
    sets = defaultdict(list)
    reads = defaultdict(list)
    for t in talks:
        for f, ws in t.sets.items():
            for w in ws:
                sets[f].append(("talk", t, w))
        for f, ws in t.reads.items():
            for w in ws:
                reads[f].append(("talk", t, w))
    for c in chapters:
        for f, ws in c.sets.items():
            for w in ws:
                sets[f].append(("scene", c, w))
        for f, ws in c.reads.items():
            for w in ws:
                reads[f].append(("scene", c, w))
    for f, ws in code.sets.items():
        for w in ws:
            sets[f].append(("code", None, w))
    for f, ws in code.reads.items():
        for w in ws:
            reads[f].append(("code", None, w))
    for v in glob.glob(os.path.join(ROOT, "game/**/visitors/*.tres"), recursive=True):
        src = open(v, encoding="utf-8").read()
        m = re.search(r'^flag = &"([a-z0-9_]+)"', src, re.M)
        if m:
            sets[m.group(1)].append(("visitor", None, rel(v)))
        m = re.search(r'^only_if = &"([a-z0-9_]+)"', src, re.M)
        if m:
            reads[m.group(1)].append(("visitor", None, rel(v)))

    def how_set(name):
        if name in sets:
            return sets[name]
        m = re.match(r"n(\d)_(.+)$", name)
        if m and m.group(2) in code.tonight_all:
            return [("code", None, "%s (every night, as n<night>_%s)" % (w, m.group(2))) for w in code.tonight_all[m.group(2)]]
        if name.startswith("n*_") and name[3:] in code.tonight_all:
            return [("code", None, w) for w in code.tonight_all[name[3:]]]
        for suffix, files in code.suffixes.items():
            if name.endswith(suffix) and len(name) > len(suffix):
                return [("family", None, "%s (built as <flag>%s)" % (f, suffix)) for f in sorted(files)]
        if m:
            for prefix, files in code.tonight_families.items():
                if m.group(2).startswith(prefix):
                    return [("family", None, "%s (built as n<night>_%s<who>)" % (f, prefix)) for f in sorted(files)]
        for prefix, files in code.families.items():
            if prefix != "night" and name.startswith(prefix):
                return [("family", None, "%s (built as %s<id>)" % (f, prefix)) for f in sorted(files)]
        if re.match(r"night\d_done$", name) and code.families.get("night"):
            return [("family", None, f) for f in sorted(code.families["night"])]
        if name.startswith("talked_"):
            return [("system", None, "a conversation's id")]
        return []

    out = OrderedDict()
    for name in sorted(set(sets) | set(reads)):
        out[name] = {"set": how_set(name), "read": reads.get(name, [])}
    return out


def where_text(kind, owner, where):
    if kind == "talk":
        return "%s, %s (`%s`)" % (display(owner.person), owner.chapter, where)
    if kind == "scene":
        return "scene: %s" % where
    return "%s: `%s`" % (kind, where)


def load_all():
    talks = load_talks()
    chapters = load_chapters()
    code = Code()
    links = build_links(talks, chapters, code)
    return talks, chapters, code, links
