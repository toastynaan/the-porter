class_name Conversation
extends Resource
## A conversation with someone (design doc, "Dialogue with memory":
## conversations that read and set flags), written as a short script in
## `text`, to edit in the inspector or any text editor. Talk.converse() plays
## it: they say their lines, and the porter picks one of up to three answers
## or walks away.
##
##   # A note; ignored.
##   == start                  A point in the talk. It starts at the first
##                             point, or at "again" once he has talked to them.
##   Osric: (Bread, brother?)  Someone says a line: "Name: line".
##   (He smells of the ovens.) A line with no name: what the porter notices.
##   * Thank him. -> end       An answer, and where it leads: a point, or end.
##                             At most three. The point's last line stays up
##                             while he chooses.
##   -> topics                 Goes on to another point with no answer asked.
##   -> merchant [if died_merchant]
##                             Goes there only if the tags hold; the first
##                             such line that holds is taken, else a plain
##                             "-> point" after them, else the talk ends.
##   == leave                  Said as he walks away in the middle of a talk.
##
## Who they are to the porter (docs/systems/mechanics.md, "Trust"): a talk starts at
## "start_warm" if they trust him 30 or more, "start_cold" below 0, else
## "start" (and "again_warm", "again_cold", "again" the next time), where
## those points exist: the greeting follows trust.
##
## Tags in square brackets, on an answer or after a point's name:
##   [if flag] [if not flag] [if flag=value]   offered only then (answers)
##   [if trust 30] [if not trust 30]           only if they trust him 30+
##   [if night=2]                              only on that night
##   [set flag] [set flag=value]               sets a GameState flag
##   [suspicion 5]                             raises Suspicion
##   [item mab_bread]                          puts something in his satchel
##   [note thomas_saw_simon]                   writes a clue in his notes
##   [trust mab 5]                             changes what someone thinks of him
##   [warn]                                    warns them (Warnings)
##   [follow] [wait]                           they follow him, or wait (Companion)
##   [drink]                                   he drinks an ale (GameState.drink)
## Every talk sets the flag talked_<id>.

const MAX_ANSWERS := 3
const END := "end"
const AGAIN := "again"
const LEAVE := "leave"
## Trust from which they greet him warmly and tell him more; below 0, coldly.
const WARM := 30

## Who he is talking to now (Talk.converse sets it): their People id, and
## the node, for [trust], [warn], [follow] and [wait].
static var partner := &""
static var partner_node: Node3D


class Line:
	var speaker := ""
	var text := ""


class Answer:
	var text := ""
	var to := ""
	var tags := PackedStringArray()


class Point:
	var name := ""
	var lines: Array[Line] = []
	var answers: Array[Answer] = []
	## Where it goes with no answer ("" or "end": the talk is over).
	var next := ""
	## Jumps that need their tags to hold: [to, tags], first that holds wins.
	var branches: Array = []
	var tags := PackedStringArray()

	## Where it goes now with no answer: the first branch that holds, else next.
	func go() -> String:
		for b: Array in branches:
			if Conversation.holds(b[1]):
				return b[0]
		return next


## Names the talked_<id> flag; the file's name if empty.
@export var id := &""
@export_multiline var text := ""

var _parsed_text := ""
var _points := {}
var _first := ""
var _errors := PackedStringArray()


## The flag set once he has talked to them.
func talked_flag() -> StringName:
	var key := String(id) if id != &"" else resource_path.get_file().get_basename()
	return StringName("talked_" + key)


## Where a talk starts: the first point, or "again" if he has talked to them,
## warm or cold by what they think of him.
func start(talked_before: bool, who := &"") -> String:
	_parse()
	var base := AGAIN if talked_before and _points.has(AGAIN) else _first
	if who != &"" and (base == AGAIN or base == "start"):
		var t := GameState.trust_of(who)
		if t >= WARM and _points.has(base + "_warm"):
			return base + "_warm"
		if t < 0 and _points.has(base + "_cold"):
			return base + "_cold"
	return base


func has_point(point_name: String) -> bool:
	_parse()
	return _points.has(point_name)


func point(point_name: String) -> Point:
	_parse()
	return _points.get(point_name) as Point


## The answers of `p` whose conditions hold now.
func offered(p: Point) -> Array[Answer]:
	var out: Array[Answer] = []
	for a in p.answers:
		if holds(a.tags):
			out.append(a)
	return out


## What is wrong with the script: unknown points, too many answers, bad tags.
func errors() -> PackedStringArray:
	_parse()
	return _errors


## True if every [if ...] tag holds.
static func holds(tags: PackedStringArray) -> bool:
	for tag in tags:
		var words := tag.split(" ", false)
		if words[0] != "if":
			continue
		var negate := words.size() >= 3 and words[1] == "not"
		var cond := words[-1]
		var ok: bool
		if words[-2] == "trust":
			ok = GameState.trust_of(partner) >= int(cond)
		elif cond.begins_with("night="):
			ok = GameState.night == int(cond.trim_prefix("night="))
		elif "=" in cond:
			var parts := cond.split("=")
			ok = str(GameState.get_flag(StringName(parts[0]), "")) == parts[1]
		else:
			# A flag, or a clue in his notes (osric_mask: he has seen Osric's face).
			var v: Variant = GameState.get_flag(StringName(cond), false)
			ok = (v != null and not (typeof(v) == TYPE_BOOL and not v)) or GameState.has_note(StringName(cond))
		if ok == negate:
			return false
	return true


## Does the [set ...] and [suspicion ...] tags.
static func apply(tags: PackedStringArray) -> void:
	for tag in tags:
		var words := tag.split(" ", false)
		match words[0]:
			"set":
				var parts := words[1].split("=")
				var value: Variant = true
				if parts.size() > 1:
					value = StringName(parts[1])
				GameState.set_flag(StringName(parts[0]), value)
			"suspicion":
				GameState.raise_suspicion(int(words[1]))
			"item":
				if not GameState.satchel.has(StringName(words[1])):
					GameState.satchel.append(StringName(words[1]))
			"note":
				GameState.note(StringName(words[1]))
			"trust":
				GameState.change_trust(StringName(words[1]), int(words[2]))
			"warn":
				Warnings.give(partner, partner_node)
			"drink":
				GameState.have_a_drink()
			"follow", "wait":
				var c := partner_node.get_node_or_null(^"Companion") as Companion if partner_node else null
				if c:
					c.set_following(words[0] == "follow")


func _parse() -> void:
	if text == _parsed_text and not _points.is_empty():
		return
	_parsed_text = text
	_points = {}
	_first = ""
	_errors = PackedStringArray()
	var current: Point = null
	var n := 0
	for raw in text.split("\n"):
		n += 1
		var line := raw.strip_edges()
		if line.is_empty() or line.begins_with("#"):
			continue
		if line.begins_with("=="):
			var head := _split_tags(line.trim_prefix("==").strip_edges(), n)
			current = Point.new()
			current.name = head[0]
			current.tags = head[1]
			if _points.has(current.name):
				_errors.append("line %d: a second point called %s" % [n, current.name])
			_points[current.name] = current
			if _first.is_empty() and current.name != LEAVE and current.name != AGAIN:
				_first = current.name
		elif current == null:
			_errors.append("line %d: everything goes under a point (== name)" % n)
		elif line.begins_with("*"):
			var body := line.trim_prefix("*").strip_edges()
			var arrow := body.rfind("->")
			var a := Answer.new()
			if arrow < 0:
				_errors.append("line %d: an answer needs -> and where it leads" % n)
				a.to = END
			else:
				a.to = body.substr(arrow + 2).strip_edges()
				body = body.substr(0, arrow).strip_edges()
			var split := _split_tags(body, n)
			a.text = split[0]
			a.tags = split[1]
			current.answers.append(a)
		elif line.begins_with("->"):
			var jump := _split_tags(line.trim_prefix("->").strip_edges(), n)
			if (jump[1] as PackedStringArray).is_empty():
				current.next = jump[0]
			else:
				current.branches.append([jump[0], jump[1]])
		else:
			var l := Line.new()
			var colon := line.find(":")
			# "Name: line" when the name comes before any bracket.
			if colon > 0 and not line.substr(0, colon).contains("("):
				l.speaker = line.substr(0, colon).strip_edges()
				l.text = line.substr(colon + 1).strip_edges()
			else:
				l.text = line
			current.lines.append(l)
	if _first.is_empty():
		_errors.append("no points")
	for p: Point in _points.values():
		if p.answers.size() > MAX_ANSWERS:
			_errors.append("%s: %d answers (three at most)" % [p.name, p.answers.size()])
		if not p.answers.is_empty() and (not p.next.is_empty() or not p.branches.is_empty()):
			_errors.append("%s: both answers and ->" % p.name)
		var targets := [p.next] if not p.next.is_empty() else []
		for b: Array in p.branches:
			targets.append(b[0])
		for a in p.answers:
			targets.append(a.to)
		for t: String in targets:
			if t != END and not _points.has(t):
				_errors.append("%s: no point called %s" % [p.name, t])


## Splits "text [tag] [tag]" into [text, tags]; checks each tag.
func _split_tags(s: String, n: int) -> Array:
	var tags := PackedStringArray()
	var out := ""
	var i := 0
	while i < s.length():
		var open := s.find("[", i)
		if open < 0:
			out += s.substr(i)
			break
		var close := s.find("]", open)
		if close < 0:
			_errors.append("line %d: a [ with no ]" % n)
			out += s.substr(i)
			break
		out += s.substr(i, open - i)
		var tag := s.substr(open + 1, close - open - 1).strip_edges()
		var words := tag.split(" ", false)
		var ok := (words.size() == 1 and words[0] in ["warn", "follow", "wait", "drink"]) or words.size() >= 2 and (
			(words[0] == "if" and (words.size() == 2 or (words.size() == 3 and words[1] == "not")
				or (words.size() == 3 and words[1] == "trust" and words[2].is_valid_int())
				or (words.size() == 4 and words[1] == "not" and words[2] == "trust" and words[3].is_valid_int())))
			or (words[0] == "set" and words.size() == 2)
			or (words[0] == "suspicion" and words.size() == 2 and words[1].is_valid_int())
			or (words[0] == "item" and words.size() == 2 and Items.ALL.has(StringName(words[1])))
			or (words[0] == "note" and words.size() == 2 and Clues.is_clue(StringName(words[1])))
			or (words[0] == "trust" and words.size() == 3 and words[2].is_valid_int()))
		if not ok:
			_errors.append("line %d: unknown tag [%s]" % [n, tag])
		else:
			tags.append(tag)
		i = close + 1
	return [out.strip_edges(), tags]
