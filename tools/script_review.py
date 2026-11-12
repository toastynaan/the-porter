#!/usr/bin/env python3
"""A review page for one chapter's script, to read and work through
together: the night's map, every conversation's paths, every line with its
face, and the flags the chapter touches. The same diagrams as docs/script/
(tools/script_docs.py), as one HTML page.

  tools/script_review.py night0              -> art/_review/script/night0.html
  tools/script_review.py night0 <out.html>
"""
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import script_model as M  # noqa: E402
import script_docs as D  # noqa: E402


def mermaid(fenced):
    body = re.sub(r"^```mermaid\n|\n```$", "", fenced.strip())
    return '<pre class="mermaid">%s</pre>' % html.escape(body)


def md_inline(text):
    """The few Markdown marks the docs writer uses, as HTML."""
    t = html.escape(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*(.+?)\*", r"<em>\1</em>", t)
    return t


def flag_chip(f):
    return '<a class="flag" href="#flag-%s">%s</a>' % (D.anchor(f), html.escape(f))


def lines_html(talk):
    out = []
    for name, p in talk.points.items():
        claim = M.claim_of(p["tags"])
        cls = "point claim" if claim else "point"
        out.append('<section class="%s" id="pt-%s-%s">' % (cls, D.anchor(talk.file), D.anchor(name)))
        head = '<h5><code>%s</code>%s</h5>' % (html.escape(name), " <span class='muted'>the next time</span>" if name == "again"
                                                else " <span class='muted'>if he walks away</span>" if name == "leave" else "")
        out.append(head)
        extra = D.conditions(p["tags"]) and ["only if " + ", ".join(D.conditions(p["tags"]))] or []
        extra += D.effects(p["tags"])
        if extra:
            out.append('<p class="effects">%s</p>' % md_inline("; ".join(extra)))
        out.append("<ul class='lines'>")
        for l in p["lines"]:
            if l["who"]:
                face = ", ".join([l["mood"]] + l["tells"]) if l["mood"] else "no face"
                out.append("<li><span class='who'>%s</span> <span class='face'>%s</span> %s</li>" % (
                    html.escape(l["who"]), html.escape(face), md_inline(l["text"])))
            else:
                out.append("<li class='narration'>%s</li>" % md_inline(l["text"].strip("()")))
        out.append("</ul>")
        if claim:
            out.append("<p class='claimnote'>Claim <code>%s</code>: %s. The last line is the claim.</p>" % (
                html.escape(claim[0]), html.escape(M.TRUTH_WORDS.get(claim[1], claim[1]))))
        if p["answers"]:
            out.append("<ol class='answers'>")
            for a in p["answers"]:
                stance, proof = M.stance_of(a["tags"])
                bits = []
                if stance:
                    right = claim and stance in M.RIGHT.get(claim[1], [])
                    bits.append("<span class='stance %s'>%s%s</span>" % ("right" if right else "wrong", stance,
                                                                        (" with " + html.escape(proof)) if proof else ""))
                conds = D.conditions(a["tags"])
                if conds:
                    bits.append(md_inline("only if " + ", ".join(conds)))
                bits += [md_inline(e) for e in D.effects(a["tags"])]
                if stance and claim:
                    bits.append(md_inline(D.read_outcome(claim[1], stance, talk.person)))
                out.append("<li>%s <span class='to'>→ <code>%s</code></span>%s</li>" % (
                    md_inline(a["text"]), html.escape(a["to"]), ("<span class='bits'>" + " · ".join(bits) + "</span>") if bits else ""))
            out.append("</ol>")
        for j in p["jumps"]:
            conds = D.conditions(j["tags"])
            out.append("<p class='jump'>→ <code>%s</code>%s</p>" % (html.escape(j["to"]), md_inline(" if " + ", ".join(conds)) if conds else ""))
        out.append("</section>")
    return "\n".join(out)


def talk_block(talk, links):
    who = talk.person
    title = M.display(who) if talk.file == who else "%s <span class='muted'>(%s)</span>" % (html.escape(M.display(who)), html.escape(talk.file.replace("_", " ")))
    chips = ["<span class='chip mono'>%s</span>" % html.escape(os.path.basename(talk.path)), "<span class='chip mono'>id %s</span>" % html.escape(talk.id)]
    b = M.BASELINES.get(who)
    if b:
        chips.append("<span class='chip'>baseline <em>%s</em>%s</span>" % (html.escape(b.get("mood", "")), (", habit <em>%s</em>" % html.escape(b["habit"])) if "habit" in b else ""))
    if who in M.START_TRUST:
        chips.append("<span class='chip'>trust %d</span>" % M.START_TRUST[who])
    if who in M.CULT:
        chips.append("<span class='chip cult'>in the cult</span>")
    claims = talk.claims()
    if claims:
        chips.append("<span class='chip claimchip'>%d claim%s</span>" % (len(claims), "" if len(claims) == 1 else "s"))
    moods = [l["mood"] for p in talk.points.values() for l in p["lines"] if l["mood"]]
    ins = sorted(f for f in talk.reads if f not in talk.sets)
    outs = sorted(f for f in talk.sets if not f.startswith("talked_") and any(r[1] is not talk for r in links.get(f, {}).get("read", [])))
    parts = ['<article class="talk" id="talk-%s">' % D.anchor(talk.file)]
    parts.append("<header><h3>%s</h3><div class='chips'>%s</div></header>" % (title if talk.file != who else html.escape(title), "".join(chips)))
    for n in talk.notes:
        parts.append("<p class='note'>%s</p>" % md_inline(n))
    if moods:
        parts.append("<p class='moods'><span class='label'>Moods</span> %s</p>" % " → ".join("<em>%s</em>" % html.escape(m) for m in D.runs(moods)))
    if ins or outs:
        parts.append("<div class='linkrow'>")
        if ins:
            parts.append("<p><span class='label'>Reads from elsewhere</span> %s</p>" % " ".join(flag_chip(f) for f in ins))
        if outs:
            parts.append("<p><span class='label'>Read elsewhere</span> %s</p>" % " ".join(flag_chip(f) for f in outs))
        parts.append("</div>")
    parts.append('<div class="diagram">%s</div>' % mermaid(D.flowchart(talk)))
    parts.append("<details><summary>Every line, with faces and effects</summary>%s</details>" % lines_html(talk))
    parts.append("</article>")
    return "\n".join(parts)


def flags_table(chapter_talks, chapter, links):
    names = set()
    for t in chapter_talks:
        names |= {f for f in t.sets if not f.startswith("talked_")} | set(t.reads)
    for b in chapter.beats:
        names |= set(b["sets"])
    rows = []
    for f in sorted(names):
        v = links.get(f)
        if not v:
            continue
        def cell(ws):
            return "<br>".join(md_inline(M.where_text(*w)) for w in ws) if ws else "<span class='warn'>nothing</span>"
        rows.append("<tr id='flag-%s'><td><code>%s</code>%s</td><td>%s</td><td>%s</td></tr>" % (
            D.anchor(f), html.escape(f), "<div class='muted small'>note: %s</div>" % html.escape(M.CLUES[f]) if f in M.CLUES else "",
            cell(v["set"]), cell(v["read"])))
    return "<div class='tablewrap'><table><thead><tr><th>Flag or note</th><th>Set by</th><th>Read by</th></tr></thead><tbody>%s</tbody></table></div>" % "".join(rows)


CSS = """
:root{
  /* A porter's ledger: ink on vellum by day, lamplight on slate by night. Running text left, index right on wide screens. */
  --bg:#f6f4ef; --panel:#fffdf8; --fg:#1f2328; --muted:#5d6470; --line:#d9d4c7;
  --accent:#7a2e2b; --accent-soft:#f1dfd9; --claim:#9a6b1a; --claim-soft:#f6ead0;
  --right:#2f6b3d; --wrong:#a3392f; --code:#efeae0;
  --display:"EB Garamond", Georgia, "Times New Roman", serif;
  --body:"Source Sans 3", "Segoe UI", system-ui, sans-serif;
  --mono:"IBM Plex Mono", ui-monospace, Menlo, monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#171a1f; --panel:#1e2228; --fg:#e8e4da; --muted:#a3a9b3; --line:#343a43;
  --accent:#e09a8f; --accent-soft:#3a2523; --claim:#e0b45e; --claim-soft:#382d17;
  --right:#7cc48b; --wrong:#ef8a7f; --code:#262b33; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#171a1f; --panel:#1e2228; --fg:#e8e4da; --muted:#a3a9b3; --line:#343a43;
  --accent:#e09a8f; --accent-soft:#3a2523; --claim:#e0b45e; --claim-soft:#382d17;
  --right:#7cc48b; --wrong:#ef8a7f; --code:#262b33; color-scheme:dark}
body{background:var(--bg);color:var(--fg);font:16px/1.55 var(--body);}
.page{max-width:1240px;margin:0 auto;padding-block:28px 64px;padding-left:max(16px, env(safe-area-inset-left, 0px));padding-right:max(16px, env(safe-area-inset-right, 0px));display:grid;grid-template-columns:minmax(0,1fr) 230px;gap:40px}
@media (max-width:900px){.page{grid-template-columns:minmax(0,1fr)}.index{display:none}}
main{min-width:0}
h1,h2,h3{font-family:var(--display);font-weight:600;text-wrap:balance;line-height:1.15}
h1{font-size:2.4rem;margin:.1em 0 .2em}
h2{font-size:1.7rem;margin:2.2em 0 .5em;padding-top:.4em;border-top:1px solid var(--line)}
h3{font-size:1.45rem;margin:0}
.eyebrow{font:600 .78rem/1 var(--body);letter-spacing:.12em;text-transform:uppercase;color:var(--accent)}
.lead{max-width:68ch;color:var(--muted)}
.muted{color:var(--muted)} .small{font-size:.85em}
code,.mono{font-family:var(--mono);font-size:.86em}
code{background:var(--code);padding:.05em .35em;border-radius:3px}
.legend{display:flex;flex-wrap:wrap;gap:8px 18px;margin:18px 0 0;font-size:.88rem;color:var(--muted)}
.legend span{display:inline-flex;align-items:center;gap:6px}
.sw{width:22px;height:0;border-top:3px solid}
.sw.right{border-color:var(--right)} .sw.wrong{border-color:var(--wrong)} .sw.dot{border-top-style:dotted;border-color:var(--muted)}
.hex{width:14px;height:12px;background:var(--claim-soft);border:1.5px solid var(--claim);clip-path:polygon(25% 0,75% 0,100% 50%,75% 100%,25% 100%,0 50%)}
.diagram{overflow-x:auto;background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:14px;margin:12px 0}
.diagram pre{margin:0}
.talk{padding:22px 0 8px;border-top:1px solid var(--line)}
.talk header{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px 14px}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{font-size:.78rem;padding:2px 8px;border:1px solid var(--line);border-radius:999px;color:var(--muted);background:var(--panel)}
.chip.cult{border-color:var(--accent);color:var(--accent);background:var(--accent-soft)}
.chip.claimchip{border-color:var(--claim);color:var(--claim);background:var(--claim-soft)}
.note{margin:.5em 0;color:var(--muted);max-width:75ch;font-size:.93rem}
.moods{margin:.4em 0;font-size:.93rem}
.label{font:600 .72rem/1 var(--body);letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-right:8px}
.linkrow p{margin:.35em 0}
.flag{font-family:var(--mono);font-size:.8rem;color:var(--accent);text-decoration:none;border-bottom:1px dotted var(--accent);margin-right:8px;white-space:nowrap}
details{margin:8px 0 18px}
summary{cursor:pointer;color:var(--accent);font-weight:600}
summary:focus-visible,a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.point{margin:14px 0;padding-left:12px;border-left:2px solid var(--line)}
.point.claim{border-left-color:var(--claim);background:linear-gradient(90deg,var(--claim-soft),transparent 60%)}
.point h5{margin:.2em 0;font-size:.95rem}
.effects{margin:.2em 0;font-size:.88rem;color:var(--muted)}
.lines{list-style:none;padding:0;margin:.3em 0}
.lines li{margin:.25em 0;max-width:80ch}
.who{font-variant:small-caps;letter-spacing:.04em;font-weight:600;color:var(--accent)}
.face{font-style:italic;font-size:.85em;color:var(--muted)}
.face::before{content:"{"} .face::after{content:"}"}
.narration{font-style:italic;color:var(--muted)}
.claimnote{font-size:.9rem;color:var(--claim);font-weight:600}
.answers{margin:.3em 0 .3em 1.2em;padding:0}
.answers li{margin:.3em 0;max-width:85ch}
.to{color:var(--muted);font-size:.9em;margin-left:4px}
.bits{display:block;font-size:.84rem;color:var(--muted)}
.stance{font-family:var(--mono);font-size:.78rem;padding:0 6px;border-radius:3px;border:1px solid}
.stance.right{color:var(--right);border-color:var(--right)} .stance.wrong{color:var(--wrong);border-color:var(--wrong)}
.jump{margin:.2em 0;font-size:.9rem;color:var(--muted)}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:6px;background:var(--panel)}
table{border-collapse:collapse;width:100%;font-size:.86rem}
th,td{text-align:left;vertical-align:top;padding:8px 10px;border-bottom:1px solid var(--line)}
th{font-weight:600;color:var(--muted);position:sticky;top:0;background:var(--panel)}
td:first-child{white-space:nowrap}
.warn{color:var(--wrong);font-weight:600}
.index{position:sticky;top:max(20px, env(safe-area-inset-top, 0px));align-self:start;max-height:calc(100vh - 40px);overflow:auto;font-size:.88rem}
.index h4{font:600 .72rem/1 var(--body);letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin:0 0 10px}
.index a{display:block;color:var(--fg);text-decoration:none;padding:3px 0}
.index a:hover{color:var(--accent)}
.index .sub{padding-left:12px;color:var(--muted)}
@media (prefers-reduced-motion: reduce){*{scroll-behavior:auto}}
"""


def page(chapter_id):
    talks, chapters, code, links = M.load_all()
    chapter = next(c for c in chapters if c.id == chapter_id)
    talks_by_path = {t.path: t for t in talks}
    mine = [t for t in talks if t.chapter == chapter_id]
    # In the order the night meets them: talks the beats open, then the rest.
    order = [p for b in chapter.beats for p in b["talks"]] + [t["talk"] for t in chapter.talkers]
    mine.sort(key=lambda t: order.index(t.path) if t.path in order else 999)
    title = "%s: %s" % (chapter.heading.capitalize(), chapter.title) if chapter.heading else chapter.title
    claims = sum(len(t.claims()) for t in mine)
    body = []
    body.append("<header><div class='eyebrow'>The Porter · script review</div><h1>%s</h1>" % html.escape(title))
    body.append("<p class='lead'>Night %d, as the game plays it: the night's beats in order and who Alric can talk to when, then every conversation's paths, its lines and faces, and the flags it shares with the rest of the game. %d conversations, %d claims. Generated from the game's files by <code>tools/script_review.py</code>.</p>" % (chapter.night, len(mine), claims))
    body.append("<div class='legend'><span><i class='sw right'></i>right read</span><span><i class='sw wrong'></i>wrong read</span><span><i class='sw dot'></i>a jump with no answer</span><span><i class='hex'></i>a claim</span></div></header>")
    body.append("<h2 id='night'>The night</h2>")
    body.append("<p class='lead'>The beats run down the page in order. A solid arrow from <em>The night</em> is a talk that a beat opens itself; one from <em>Alric</em> is someone he can go and talk to from then on. A dashed arrow is a flag one talk sets and another reads. Within a beat the order of its talks is the order they're named in the scene, not always the order they happen: on the ride it is the road talk, the cart, Aldgate, then the carter at the gate.</p>")
    body.append('<div class="diagram">%s</div>' % mermaid(D.night_map(chapter, talks_by_path, links)))
    body.append("<h2 id='talks'>Conversations</h2>")
    for t in mine:
        body.append(talk_block(t, links))
    body.append("<h2 id='flags'>Flags and notes this night touches</h2>")
    body.append("<p class='lead'>Everything the night's talks and beats set or read, with where else in the game it's set and read. A note is a line in Alric's ledger.</p>")
    body.append(flags_table(mine, chapter, links))
    index = ["<nav class='index' aria-label='On this page'><h4>On this page</h4><a href='#night'>The night</a><a href='#talks'>Conversations</a>"]
    for t in mine:
        index.append("<a class='sub' href='#talk-%s'>%s</a>" % (D.anchor(t.file), html.escape(M.display(t.person) + ("" if t.file == t.person else " (%s)" % t.file.replace("_", " ")))))
    index.append("<a href='#flags'>Flags and notes</a></nav>")
    head = ('<title>%s Script Review</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@500;600&family=IBM+Plex+Mono:wght@400;500&family=Source+Sans+3:ital,wght@0,400;0,600;1,400&display=swap">\n'
            "<style>%s</style>\n") % (html.escape(chapter.title), CSS)
    return head + "<div class='page'><main>%s</main>%s</div>\n" % ("\n".join(body), "\n".join(index))


def main():
    chapter = sys.argv[1] if len(sys.argv) > 1 else "night0"
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(M.ROOT, "art/_review/script/%s.html" % chapter)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(page(chapter))
    print("wrote", os.path.relpath(out, M.ROOT) if out.startswith(M.ROOT) else out)


if __name__ == "__main__":
    main()
