@tool
class_name PersonModel
extends Node3D
## A character scene with a real model (game/characters/chr_<name>.tscn;
## tools/build/people.py, tools/build/rig.py): Model, his body on its
## skeleton with the clips it moves by; Head, his face (a FaceRig over the
## head model); Face, the marker the talk looks at. In the game, Head and
## Face ride on the skeleton's head bone.
##
## The clips (Look and Feel, "PSX": in steps at 15 a second, like every
## character): idle standing; talk while his face speaks; walk as he is
## carried along on his feet, at the pace he goes; sit and sit_talk when
## `seated` (the seat at the origin). A clip he doesn't have falls back to
## the nearest he has (sit_talk to sit, talk to idle). Parts of his model
## named Reins and Whip (the carter's, made as he drives) show only as he sits.
##
## A hand can hold a part of the scene (the warden's lantern and staff): the
## arm reaches for it wherever a beat puts it (HandReach), and if it is out
## of reach it comes back into the hand.

## Steps a second, as every character moves.
const STEP := 1.0 / 15.0
## Where the Face marker is from the neck: between the eyes, at the face.
const FACE_FROM_NECK := Vector3(0.0, 0.17, -0.1)
## Carried faster than this (m/s) standing, he walks.
const WALKING := 0.25
## The pace of the walk clip at its own speed, m/s *(mine)*.
const WALK_PACE := 1.3
## Seconds one clip blends into the next.
const BLEND := 0.3

## Sitting (on the wagon, at a table): his seated clips, the seat at the origin.
@export var seated := false:
	set(value):
		seated = value
		_play(_wanted(), true)
## The part of this scene his right hand holds (the warden's Lantern), or
## empty. Its origin is where the hand holds it.
@export var right_hand_holds: NodePath
## The part his left hand holds (the warden's Staff), or empty.
@export var left_hand_holds: NodePath
## Which way his right elbow goes as that arm reaches (this scene's space;
## the left's is mirrored).
@export var elbow_toward := Vector3(0.5, -1.0, 0.35)

var _anim: AnimationPlayer
var _skeleton: Skeleton3D
var _face: FaceRig
var _acc := 0.0
var _last := Vector3.INF
var _speed := 0.0
var _clip := &""


func _ready() -> void:
	_anim = find_child("AnimationPlayer", true, false) as AnimationPlayer
	_skeleton = find_child("Skeleton3D", true, false) as Skeleton3D
	_face = get_node_or_null(^"Head") as FaceRig
	if _anim:
		_anim.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
		for n in _anim.get_animation_list():
			_anim.get_animation(n).loop_mode = Animation.LOOP_LINEAR
	# Editing this scene itself, it stays as saved; anywhere else (in the
	# game, or as another scene's look) the head rides on the skeleton.
	var editing_me := Engine.is_editor_hint() and get_tree().edited_scene_root == self
	if not editing_me:
		_mount_head()
	_play(_wanted(), true)
	if Engine.is_editor_hint():
		return
	for side in [&"r", &"l"]:
		var path := right_hand_holds if side == &"r" else left_hand_holds
		var held := get_node_or_null(path) as Node3D if not path.is_empty() else null
		if held and _skeleton:
			var reach := HandReach.new()
			reach.side = side
			reach.held = held
			reach.person = self
			var pole := elbow_toward
			reach.elbow_toward = pole if side == &"r" else Vector3(-pole.x, pole.y, pole.z)
			_skeleton.add_child(reach)


## Head and Face onto the skeleton's head bone, as they are at its rest.
func _mount_head() -> void:
	if _skeleton == null:
		return
	var bone := _skeleton.find_bone("Head")
	var neck_bone := _skeleton.find_bone("neck_01")
	if bone < 0 or neck_bone < 0:
		return
	var here := _in_here(_skeleton)
	var rest := here * _skeleton.get_bone_global_rest(bone)
	var neck := (here * _skeleton.get_bone_global_rest(neck_bone)).origin
	var bone_mount := BoneAttachment3D.new()
	bone_mount.name = "HeadBone"
	_skeleton.add_child(bone_mount)
	bone_mount.bone_name = "Head"
	# Upright in this scene's space at the bone's rest (the FaceRig turns
	# its own node from upright).
	var mount := Node3D.new()
	mount.name = "Upright"
	bone_mount.add_child(mount)
	mount.transform = rest.affine_inverse()
	var head := get_node_or_null(^"Head") as Node3D
	if head:
		head.reparent(mount, false)
		head.transform = Transform3D(Basis(), neck)
	var face := get_node_or_null(^"Face") as Node3D
	if face:
		face.reparent(mount, false)
		face.transform = Transform3D(Basis(), neck + FACE_FROM_NECK)


## A node's transform in this scene's space, from its parents' (it may not
## be in the tree yet).
func _in_here(n: Node3D) -> Transform3D:
	var t := Transform3D.IDENTITY
	var at: Node = n
	while at and at != self:
		if at is Node3D:
			t = (at as Node3D).transform * t
		at = at.get_parent()
	return t


## The face the talk looks at (on the head bone in the game).
func face_marker() -> Node3D:
	return find_child("Face", true, false) as Node3D


func _wanted() -> StringName:
	var talking := _face != null and _face.speaking()
	if seated:
		return &"sit_talk" if talking else &"sit"
	if _speed > WALKING and global_basis.y.normalized().y > 0.9:
		return &"walk"
	return &"talk" if talking else &"idle"


func _play(clip: StringName, at_once := false) -> void:
	if _anim == null:
		return
	for part_name in ["Reins", "Whip"]:
		var part := find_child(part_name, true, false) as Node3D
		if part:
			part.visible = seated
	for fallback in [clip, &"sit" if seated else &"idle", &"idle"]:
		if _anim.has_animation(fallback):
			clip = fallback
			break
	if clip == _clip:
		return
	_clip = clip
	if at_once or not _anim.is_playing():
		_anim.play(clip)
		# Somewhere in the loop, so people near each other don't move as one.
		_anim.seek(randf() * _anim.current_animation_length if not Engine.is_editor_hint() else 0.0, true)
	else:
		_anim.play(clip, BLEND)


func _process(delta: float) -> void:
	if Engine.is_editor_hint():
		return
	_acc += delta
	if _acc < STEP:
		return
	var dt := _acc
	_acc = 0.0
	var at := global_position
	var moved := 0.0 if _last == Vector3.INF else Vector2(at.x - _last.x, at.z - _last.z).length()
	_last = at
	if moved > 1.0:
		# Put somewhere, not walked there.
		moved = 0.0
	_speed = moved / maxf(dt, 0.001)
	_play(_wanted())
	if _anim:
		_anim.speed_scale = clampf(_speed / WALK_PACE, 0.5, 2.0) if _clip == &"walk" else 1.0
		_anim.advance(dt)
