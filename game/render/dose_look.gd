class_name DoseLook
extends Resource
## How the image follows Dose: one curve per post-process effect, x = Dose
## (0-100), plus the fog colour. The values are the M0 proposal the user
## signed off to start from; tune them in game/render/dose_look.tres.

## Grain amplitude at black (half that at white).
@export var grain: Curve
@export var vignette: Curve
## 0 = sober palette, 1 = full drugged shift.
@export var palette_shift: Curve
## Fraction of the screen.
@export var edge_warp: Curve
## Source pixels.
@export var blur: Curve
@export var levels := 48.0
## Volumetric fog albedo, sober (Moonlight #6E7F96) and fully drugged; the fog
## moves between them with palette_shift.
@export var fog_sober := Color("6e7f96")
@export var fog_drugged := Color("7a5a70")
