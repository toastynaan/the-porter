# Working on The Porter

`README.md` has what the game is, how to run it, and where things are. This file is how we work.

## Truth

- `docs/design/` is the user's. It wins over everything. Never invent story, characters or dimensions it doesn't give: ask.
- The rest of `docs/` describes the game as built. Update it in the same commit as the change it describes.
- A number or choice the docs don't give is marked *(mine)* and logged for the user to review: in `docs/log/decisions.md`, or for rules and numbers in `docs/systems/mechanics.md`, "Decisions to review".
- New dialogue and story text is a draft: conversations start with `# DRAFT`.
- Every spoken line carries a face (`Name {mood, tells}: words`, `docs/systems/faces.md`). Check with `tools/lint_faces.py` (no Godot needed), then run `tools/script_docs.py` so `docs/script/` matches.

## Where new things go

- Used by one chapter: `game/chapters/<chapter>/` (its beats beside its scene, `dialogue/`, `visitors/`).
- Used by several chapters: the system folder it belongs to (`time/`, `duties/`, `gate/`, `talk/`, `hunting/`...). Shared beats go in `chapters/common/`.
- World content is human-editable `.tscn` scenes: Blender scripts (`tools/build/`) make meshes, scenes place them. Every asset is built by a script; `game/world/` and `game/characters/` are where those scripts write, so they don't move.
- Downloads: CC0 only (Poly Haven, ambientCG), each logged in `art/credits.csv`.
- Playtest recordings go in `playtests/` and are never committed.

## Checks

- Godot 4.8: `/Applications/Godot_4_8.app/Contents/MacOS/Godot`. Blender 5.2: `/Applications/Blender.app/Contents/MacOS/Blender`.
- `tools/check.sh` runs everything (about 20 minutes) with GDScript warnings as errors; `tools/check.sh <name>` runs the matching tests. While working, run the tests that touch the change; the full suite before a push, or when the user asks.
- A script error makes a test idle until the 900 s timeout: watch its log and stop it early.
- Headless Godot can't render. Stills and films (`tools/shots/`) open a window. Look at the stills before reporting visual work.
- The user often has the editor open. Never kill it. While it's open, run checks in a copy in the scratchpad (rsync without `.git`, `art/_review`, `.godot/editor`, `override.cfg`, with its own `custom_user_dir_name`), and copy any new `.uid` files back.
- Moving files in `game/` changes `res://` paths in scenes: do it only with the editor closed, rewrite every reference, and run the full suite.

## Commits

- One change per commit, on `main`, with a message that says what changed and why (see `git log`). Then a "Docs: ... in Progress" commit adds a line with that commit's hash to `docs/log/progress.md`.
- Never push without asking. The user also commits and pushes by hand, so check `git log origin/main..HEAD` and `git status` before assuming the tree is yours.
- Commit only your own changes. If the tree has someone else's uncommitted work, leave it out.
