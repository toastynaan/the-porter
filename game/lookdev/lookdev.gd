extends Node3D
## Look-development stage: the standard lantern (held low and to the left of
## the camera, as the player holds it), cold moonlight from behind the
## subject, the night fog, and a 1.75 m reference figure beside the subject.
## Runs inside the render pipeline (game/render/main.tscn), so every shot has
## the final look.
##
## Review mode renders the 5 review shots at Dose 0 and 75 to
## art/_review/<asset_id>/<shot>_dose<NN>.png, then quits (tools/review.sh):
##   front          straight on, eye height, lantern lit
##   three_quarter  45 degrees round, eye height, lantern lit
##   close          a near look at the upper part, lantern lit
##   silhouette     far off, lantern covered: the shape against moonlit fog
##   scale          orthographic front view beside the reference figure
## The lantern's own meshes are hidden so they never cover the subject.
##
## By hand: 1-5 pick a shot, [ and ] ease Dose down or up by 25, C covers the
## lantern.
##
## User arguments: --review, --asset-id=<id>, --asset=res://<scene or .glb>.

const SHOTS: Array[StringName] = [&"front", &"three_quarter", &"close", &"silhouette", &"scale"]
const REVIEW_DOSES: Array[float] = [0.0, 75.0]
const REVIEW_DIR := "res://art/_review"
## Camera height for the eye-level shots, m.
const EYE_HEIGHT := 1.6
## Seconds each shot waits before capture, so the lantern cover tween ends
## and the volumetric fog settles.
const SETTLE_TIME := 0.8
## Gap between the subject and the reference figure, m.
const FIGURE_GAP := 0.6

@export var asset_id := &"lookdev_baseline"

var _shot := 0

@onready var subject: Node3D = $Subject
@onready var ref_figure: Node3D = $RefFigure
@onready var camera: Camera3D = $Camera
@onready var lantern: Lantern = $Camera/Lantern


func _ready() -> void:
	var review := false
	for arg in OS.get_cmdline_user_args():
		if arg == "--review":
			review = true
		elif arg.begins_with("--asset-id="):
			asset_id = StringName(arg.trim_prefix("--asset-id="))
		elif arg.begins_with("--asset="):
			_set_subject(load(arg.trim_prefix("--asset=")))
	lantern.set_meshes_visible(false)
	var box := _subject_aabb()
	ref_figure.position = Vector3(box.end.x + FIGURE_GAP + 0.3, 0.0, box.get_center().z)
	_frame(SHOTS[_shot])
	if review:
		_review.call_deferred()


func _unhandled_input(event: InputEvent) -> void:
	var key := event as InputEventKey
	if key == null or not key.pressed or key.echo:
		return
	match key.keycode:
		KEY_1, KEY_2, KEY_3, KEY_4, KEY_5:
			_shot = key.keycode - KEY_1
			_frame(SHOTS[_shot])
		KEY_BRACKETLEFT:
			GameState.add_dose(-25.0, 2.0)
		KEY_BRACKETRIGHT:
			GameState.add_dose(25.0, 2.0)
		KEY_C:
			lantern.covered = not lantern.covered


func _review() -> void:
	var dir := "%s/%s" % [REVIEW_DIR, asset_id]
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(dir))
	lantern.freeze_flicker = true
	for dose in REVIEW_DOSES:
		GameState.snap_dose(dose)
		for shot in SHOTS:
			_frame(shot)
			await get_tree().create_timer(SETTLE_TIME).timeout
			await RenderingServer.frame_post_draw
			var img := get_tree().root.get_texture().get_image()
			# A HiDPI window is a whole multiple of 960x540: store the 540-line image.
			var s := floori(img.get_height() / 540.0)
			if s > 1:
				img.resize(roundi(img.get_width() / float(s)), roundi(img.get_height() / float(s)), Image.INTERPOLATE_NEAREST)
			var path := "%s/%s_dose%02d.png" % [dir, shot, int(dose)]
			if img.save_png(ProjectSettings.globalize_path(path)) != OK:
				push_error("lookdev: could not write %s" % path)
			else:
				print("lookdev: wrote %s" % path)
	get_tree().quit()


func _set_subject(scene: PackedScene) -> void:
	if scene == null:
		push_error("lookdev: --asset did not load")
		return
	for child in subject.get_children():
		subject.remove_child(child)
		child.queue_free()
	subject.add_child(scene.instantiate())


## Places the camera for `shot`, framing the subject's bounds.
func _frame(shot: StringName) -> void:
	var box := _subject_aabb()
	var center := box.get_center()
	var radius := maxf(box.size.length() * 0.5, 0.25)
	var dist := radius / sin(deg_to_rad(camera.fov) * 0.5) * 1.05
	var eye_y := EYE_HEIGHT if box.size.y > 1.2 else box.end.y + 0.4
	camera.projection = Camera3D.PROJECTION_PERSPECTIVE
	lantern.covered = shot == &"silhouette"
	var from := Vector3.ZERO
	var target := center
	match shot:
		&"front":
			from = Vector3(center.x, eye_y, box.end.z + dist)
		&"three_quarter":
			from = center + Vector3(sin(PI / 4.0), 0.0, cos(PI / 4.0)) * dist
			from.y = eye_y
		&"close":
			target = center + Vector3(0.0, box.size.y * 0.25, 0.0)
			from = target + Vector3(-0.35, 0.0, 1.0).normalized() * maxf(dist * 0.4, 0.8)
		&"silhouette":
			from = Vector3(center.x, EYE_HEIGHT, box.end.z + maxf(dist * 3.0, 12.0))
		&"scale":
			var both := box.merge(_aabb_of(ref_figure))
			center = both.get_center()
			camera.projection = Camera3D.PROJECTION_ORTHOGONAL
			camera.size = maxf(both.size.y, both.size.x * 540.0 / 960.0) * 1.15
			# Close enough for the lantern to light the subject.
			from = Vector3(center.x, center.y, both.end.z + 3.0)
			target = center
	camera.look_at_from_position(from, target)


func _subject_aabb() -> AABB:
	var box := _aabb_of(subject)
	return box if box.has_volume() else AABB(Vector3(-0.5, 0.0, -0.5), Vector3.ONE)


func _aabb_of(root: Node) -> AABB:
	var box := AABB()
	var first := true
	for node in root.find_children("*", "VisualInstance3D", true, false):
		var vi := node as VisualInstance3D
		var b := vi.global_transform * vi.get_aabb()
		box = b if first else box.merge(b)
		first = false
	return box
