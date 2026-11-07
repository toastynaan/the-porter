class_name DoseDriver
extends Node
## Pushes GameState.dose into the post shader and the world's fog colour
## through the DoseLook curves, every frame (Dose itself only ever drifts).
## The Environment's saturation isn't touched: the doc's saturation change is
## for reds and ambers only, which the post shader does.

@export var look: DoseLook
@export var screen: CanvasItem
@export var world: SubViewport

## 0..1 from staring at the demon; set by the stare meter (M3).
var stare := 0.0


func _process(_delta: float) -> void:
	var d := GameState.dose
	var mat := screen.material as ShaderMaterial
	var shift := look.palette_shift.sample(d)
	mat.set_shader_parameter(&"dose", d)
	mat.set_shader_parameter(&"grain", look.grain.sample(d))
	mat.set_shader_parameter(&"vignette", look.vignette.sample(d))
	mat.set_shader_parameter(&"palette_shift", shift)
	mat.set_shader_parameter(&"edge_warp", look.edge_warp.sample(d))
	mat.set_shader_parameter(&"blur", look.blur.sample(d))
	mat.set_shader_parameter(&"levels", look.levels)
	mat.set_shader_parameter(&"stare", stare)
	var env := world.find_world_3d().environment
	if env:
		env.volumetric_fog_albedo = look.fog_sober.lerp(look.fog_drugged, shift)
