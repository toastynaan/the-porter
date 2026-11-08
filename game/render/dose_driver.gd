class_name DoseDriver
extends Node
## Pushes GameState.dose into the post shader, the world's fog colour and the
## reverb on what he hears, through the DoseLook curves, every frame (Dose
## itself only ever drifts). Drink adds its own blur (1-2 ales, a softer
## focus) and a drifting double image (3 and more), and the morning after
## three or more ales, a headache blur until noon (docs/mechanics.md,
## "Drinking"; Look and Feel, "Drink and daylight": no palette shift).
## The Environment's saturation isn't touched: the doc's saturation change is
## for reds and ambers only, which the post shader does.

@export var look: DoseLook
@export var screen: CanvasItem
@export var world: SubViewport

## 0..1 from staring at the demon; set by the stare meter (group "dose_driver").
var stare := 0.0

var _reverb: AudioEffectReverb


func _ready() -> void:
	add_to_group(&"dose_driver")
	_reverb = AudioEffectReverb.new()
	_reverb.room_size = 0.85
	_reverb.damping = 0.4
	_reverb.dry = 1.0
	_reverb.wet = 0.0
	AudioServer.add_bus_effect(0, _reverb)


## Source pixels of blur from drink, and from the morning after.
static func drink_blur() -> float:
	var b := 0.0
	if GameState.drink > 0.5:
		b = 0.5 + 0.15 * minf(GameState.drink, 5.0)
	if GameState.has_flag(&"hangover") and GameState.hour < 12.0:
		b = maxf(b, 0.9)
	return b


## 0..1: the double image, from 3 ales.
static func drunk_amount() -> float:
	return clampf((GameState.drink - 2.0) / 3.0, 0.0, 1.0)


func _exit_tree() -> void:
	for i in AudioServer.get_bus_effect_count(0):
		if AudioServer.get_bus_effect(0, i) == _reverb:
			AudioServer.remove_bus_effect(0, i)
			break


func _process(_delta: float) -> void:
	var d := GameState.dose
	var mat := screen.material as ShaderMaterial
	var shift := look.palette_shift.sample(d)
	mat.set_shader_parameter(&"dose", d)
	mat.set_shader_parameter(&"grain", look.grain.sample(d))
	mat.set_shader_parameter(&"vignette", look.vignette.sample(d))
	mat.set_shader_parameter(&"palette_shift", shift)
	mat.set_shader_parameter(&"edge_warp", look.edge_warp.sample(d))
	mat.set_shader_parameter(&"blur", look.blur.sample(d) + drink_blur())
	mat.set_shader_parameter(&"drunk", drunk_amount())
	mat.set_shader_parameter(&"levels", look.levels)
	mat.set_shader_parameter(&"stare", stare)
	mat.set_shader_parameter(&"breathe", look.breathe.sample(d) if look.breathe else 0.0)
	if look.reverb:
		_reverb.wet = look.reverb.sample(d)
	var env := world.find_world_3d().environment
	if env:
		env.volumetric_fog_albedo = look.fog_sober.lerp(look.fog_drugged, shift)
