"""The people's kit, laid out to look at (tools/shots/kit_shots.sh runs
this, then renders the sheets): a figure or a head for every entry of every
catalogue in tools/build/people_kit.py, to art/_review/kit/models/, and
catalogue.json there saying what is on each sheet.

Sheets: bodies (every build, dressed alike), skins, faces (every head
shape, and the marks a face can carry), portraits (four people close),
brows, moods (one face in every mood, as the talk shows them), hair (cuts,
colours, beards), headwear, wear (outfits that between them use every
garment), colours (the cloth, hair and eye colours as chips).

Run: tools/shots/kit_shots.sh (or Blender: -b --python tools/build/kit_catalogue.py;
words after "--" build only the sheets whose names contain one)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import people
import people_kit as kit
import porter
import rig

OUT = os.path.join(porter.ROOT, "art", "_review", "kit", "models")
MAN = ["hose", "shoes", ("tunic", {"color": "undyed"})]
WOMAN = ["shoes", ("kirtle", {"color": "brown"})]


def figure(sheet, label, **spec):
    spec.setdefault("wear", MAN)
    spec["name"] = "kit_%s_%s" % (sheet, label)
    spec["only_clips"] = ("idle",)
    spec.setdefault("seed", 7)
    s = kit.build(spec, game=False)
    return {"id": "chr_" + spec["name"], "label": label.replace("_", " "), "neck": list(rig.JOINTS["neck"]), "look": _look(s)}


def head(sheet, label, **spec):
    spec["name"] = "kit_%s_%s" % (sheet, label)
    spec.setdefault("seed", 7)
    s = kit.build(spec, head_only=True)
    return {"id": "chr_" + spec["name"], "label": label.replace("_", " "), "look": _look(s)}


def _look(s):
    return {k: (v if isinstance(v, (int, float)) else list(v)) for k, v in people.face_look(s).items()}


def chips(table, pick=lambda v: v):
    return [{"label": name, "color": list(pick(v))} for name, v in table.items()]


def bodies():
    return {"kind": "figure", "views": [0, 80], "rows": 2, "items": [
        figure("bodies", name, body=name, wear=WOMAN if b.get("sex") == "f" else MAN,
               headwear=["kerchief"] if b.get("sex") == "f" else [], face="soft" if b.get("sex") == "f" else "plain")
        for name, b in kit.BODIES.items()]}


def skins():
    return {"kind": "head", "views": [0], "rows": 2, "items": [
        head("skins", name, skin=name, hair=("black" if name in ("brown", "dark", "olive") else "brown", "cropped"))
        for name in kit.SKINS]}


def faces():
    marks = [head("faces", "freckles", face="soft", freckles=1.0, hair=("red", "bowl"), age=0.1),
             head("faces", "scar", face="square", scar=1.0, age=0.6),
             head("faces", "young", face="soft", age=0.0),
             head("faces", "old", face="gaunt", age=1.0, hair=("white", "balding"), grey=0.6),
             head("faces", "blind", face="narrow", eyes="milky", age=0.9, hair=("grey", "tonsure"))]
    return {"kind": "head", "views": [0, 70], "rows": 3, "items": [head("faces", name, face=name) for name in kit.FACES] + marks}


def portraits():
    """Four people close: what a face is from in front, turned and side on."""
    return {"kind": "head", "views": [0, 40, 90], "rows": 1, "items": [
        head("portraits", "a_man", face="plain", hair=("dark", "cropped"), beard="stubble", brows="heavy", age=0.4),
        head("portraits", "an_old_man", face="gaunt", skin="weathered", hair=("grey", "balding"), beard="full", grey=0.5, age=0.9),
        head("portraits", "a_woman", face="soft", skin="pale", hair=("chestnut", "long"), eyes="grey", age=0.2),
        head("portraits", "a_brother", face="round", skin="ruddy", hair=("brown", "tonsure"), age=0.5)]}


def brows():
    return {"kind": "head", "views": [0], "rows": 2, "items": [
        head("brows", name, brows=name, hair=("dark", "cropped")) for name in kit.BROWS]}


def moods():
    names = ["calm", "warm", "glad", "amused", "grave", "sad", "weary", "afraid", "wary", "angry", "cold", "ashamed", "pleading",
             "pained", "drunk"]
    items = []
    for m in names:
        item = head("moods", m, hair=("dark", "cropped"), beard="stubble")
        item["mood"] = m
        items.append(item)
    return {"kind": "head", "views": [0], "rows": 3, "items": items}


def hair():
    items = [head("hair", style, hair=("brown", style)) for style in kit.HAIR_STYLES]
    items += [head("hair", name, hair=(name, "bowl")) for name in kit.HAIR]
    items += [head("hair", "beard_" + name, hair=("dark", "cropped"), beard=name) for name in kit.BEARDS if name != "none"]
    items += [head("hair", "grey_beard", hair=("dark", "cropped"), beard="full", grey=0.8, age=0.8)]
    return {"kind": "head", "views": [0, 110], "rows": 3, "items": items}


def headwear():
    return {"kind": "head", "views": [0, 110], "rows": 2, "items": [
        head("headwear", name, headwear=[name], face="soft" if name in ("wimple", "kerchief") else "plain")
        for name in kit.HEADWEAR]}


def wear():
    items = [
        figure("wear", "tunic", wear=["hose", "shoes", ("tunic", {"color": "russet", "belt": {"hung": ["purse", "knife"]}})]),
        figure("wear", "gown_cloak", wear=["hose", ("boots", {}), ("gown", {"color": "slate"}), ("cloak", {"color": "moss"})],
               headwear=["bycocket"]),
        figure("wear", "habit", hair=("brown", "tonsure"), wear=[("shoes", {"color": "brown"}), "habit"]),
        figure("wear", "habit_cowl_up", wear=[("shoes", {"color": "brown"}), ("habit", {"hood": "up"})], headwear=["cowl"]),
        figure("wear", "habit_stout", body="short_heavy", face="round", skin="ruddy", hair=("brown", "tonsure"),
               wear=[("shoes", {"color": "brown"}), ("habit", {"belt": {"hung": ["keys"]}})]),
        figure("wear", "jerkin_cloak_thrown", body="big", wear=[
            ("hose", {"color": "dark"}), ("boots", {"top": 0.3}), ("tunic", {"color": "dark", "collar_only": True}),
            ("jerkin", {"belt": {"cloth": "dark", "hung": ["keys"]}}), ("cloak", {"color": "dark", "hem": 0.34, "thrown": True, "hood": True})],
            headwear=["cap"], beard="full"),
        figure("wear", "hood_cape_wraps", wear=["hose", "wraps", "shoes", ("tunic", {"color": "brown", "belt": "rope"}), "cape"],
               headwear=["hood"]),
        figure("wear", "apron", body="big", skin="ruddy", face="broad", hair=("brown", "balding"),
               wear=["hose", "shoes", ("tunic", {"color": "tan"}), "apron"]),
        figure("wear", "kirtle_apron", body="woman_stout", face="soft",
               wear=["shoes", ("kirtle", {"color": "woad"}), ("apron", {"top": 1.3})], headwear=["wimple"]),
        figure("wear", "kirtle_cloak", body="woman_slight", face="sharp",
               wear=["shoes", ("kirtle", {"color": "grey", "belt": "leather"}), ("cloak", {"color": "brown", "hem": 0.3})],
               headwear=["kerchief"]),
        figure("wear", "pilgrim", body="lean", skin="weathered", beard="short",
               wear=["hose", "boots", ("gown", {"color": "undyed", "belt": {"cloth": "rope", "hung": ["rosary"]}}), "scrip",
                     ("cloak", {"color": "grey", "hem": 0.7})], headwear=["pilgrim_hat"]),
        figure("wear", "barefoot_pouch", body="tall_thin", face="gaunt",
               wear=[("tunic", {"color": "undyed", "hem": 0.4, "belt": {"cloth": "rope", "hung": ["pouch"]}})], headwear=["straw"]),
    ]
    return {"kind": "figure", "views": [0, 150], "rows": 2, "items": items}


def colours():
    return {"kind": "chips", "groups": [
        {"label": "cloth", "items": chips(kit.CLOTH)}, {"label": "skin", "items": chips(kit.SKINS, lambda v: v["skin"])},
        {"label": "hair", "items": chips(kit.HAIR)}, {"label": "eyes", "items": chips(kit.EYES)}]}


SHEETS = [("bodies", bodies), ("skins", skins), ("faces", faces), ("portraits", portraits), ("brows", brows), ("moods", moods),
          ("hair", hair), ("headwear", headwear), ("wear", wear), ("colours", colours)]


def main():
    """Every sheet, or only those whose name contains a word given after
    "--" (the others stay as they were last built)."""
    os.makedirs(OUT, exist_ok=True)
    porter.MODELS = OUT
    only = porter.argv()
    path = os.path.join(OUT, "catalogue.json")
    was = {s["name"]: s for s in json.load(open(path))["sheets"]} if only and os.path.exists(path) else {}
    sheets = []
    built = 0
    for name, make in SHEETS:
        if only and not any(word in name for word in only):
            if name in was:
                sheets.append(was[name])
            continue
        sheet = make()
        sheet["name"] = name
        sheets.append(sheet)
        built += 1
    json.dump({"sheets": sheets}, open(path, "w"), indent=1)
    print("built the kit's catalogue: %d sheets" % built)


if __name__ == "__main__":
    main()
