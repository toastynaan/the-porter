class_name Hunt
extends Node3D
## How hard the porter is hunted on a night's round, by Suspicion (design
## doc, "Thresholds"; docs/mechanics.md, "Suspicion" and "Reading the hidden
## numbers"). A night's beat calls begin() when the hunting starts (from
## night 3, Suspicion drives it every night) and end() when it's over:
## - 0-29: one costumed cultist on a patrol route; he chases what he sees
##   but doesn't search.
## - 30-59: he searches where he last saw the porter and checks the two
##   hiding spots nearest it (Hunter, as built).
## - 60-84: two hunters, and one of them waits at the gatehouse; the doors in
##   `locks` are locked (the porter needs his keys or another way round).
## - 85+: night 6's rules early: three hunters, all searching.
## Each hunter is someone (Hunter.wearer), for his voice and his face.

enum Band { WATCHED, SEARCHED, TWO, WHOLE }

const HUNTER := preload("res://game/hunter/hunter.tscn")

## Node3Ds with Marker3D children: the patrol routes, first first.
@export var routes: Array[Node3D] = []
## Where one hunter waits at 60+.
@export var gatehouse: Marker3D
## Doors the cult locks at 60+.
@export var locks: Array[Door] = []
## Who wears the costumes, in the order they're sent out.
@export var wearers: Array[StringName] = [&"ranulf", &"cole", &"dunstan"]
## However many the night sends whatever the Suspicion (night 6: the whole
## cult but Thomas, who leads the rite); 0: by the bands.
@export var count_override := 0

var hunters: Array[Hunter] = []
var band_now := Band.WATCHED


func _ready() -> void:
	add_to_group(&"hunt")


static func band(suspicion: int) -> Band:
	if suspicion >= 85:
		return Band.WHOLE
	if suspicion >= 60:
		return Band.TWO
	if suspicion >= 30:
		return Band.SEARCHED
	return Band.WATCHED


## Sends the hunters out for tonight's Suspicion.
func begin() -> void:
	end()
	band_now = band(GameState.suspicion)
	var count := 1
	match band_now:
		Band.TWO:
			count = 2
		Band.WHOLE:
			count = 3
	if count_override > 0:
		count = count_override
	for i in count:
		var h := HUNTER.instantiate() as Hunter
		h.wearer = wearers[i % wearers.size()]
		h.weapon = &"blade" if GameState.night >= 4 else &"cord"
		h.always_search = band_now == Band.WHOLE
		var route := routes[i % routes.size()] if not routes.is_empty() else null
		if band_now == Band.TWO and i == 1 and gatehouse:
			route = _route_of([gatehouse])
		h.patrol_route = route
		var start := route.get_child(0) as Node3D if route and route.get_child_count() > 0 else self
		# Where he starts is home: a reset sends him back there.
		h.transform = global_transform.affine_inverse() * Transform3D(Basis.IDENTITY, start.global_position)
		add_child(h)
		hunters.append(h)
	if band_now >= Band.TWO:
		for d in locks:
			if d and not d.is_open:
				d.locked = true
			elif d:
				d.set_open(false, true)
				d.locked = true
		GameState.set_flag(GameState.tonight("doors_locked"))


## Calls the hunters in.
func end() -> void:
	for h in hunters:
		if is_instance_valid(h):
			h.queue_free()
	hunters.clear()


## A route of one stop: where he waits.
func _route_of(points: Array[Marker3D]) -> Node3D:
	var r := Node3D.new()
	add_child(r)
	for p in points:
		var m := Marker3D.new()
		m.set_meta(&"wait", 1000.0)
		r.add_child(m)
		m.global_transform = p.global_transform
	return r
