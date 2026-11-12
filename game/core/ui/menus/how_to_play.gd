class_name HowToPlay
extends MenuPage
## How to play: the porter's work and the controls (docs/systems/mechanics.md,
## "Controls"), keyboard and mouse, then gamepad.

const TEXT := """[center][i]You are Brother Alric, the new porter.[/i][/center]
Keep the gate: answer the knocks, read who stands at the grille, and let them in, turn them away, or send for the prior. Ring the bell for Matins at midnight and count the brothers in the choir. Walk the lantern round. The candle on your desk keeps the hours; the ledger keeps the duties. A faint flame marks what your duty needs.

[b]Walk, look[/b]  WASD and the mouse  ·  the sticks
[b]Run[/b]  Shift  ·  left stick
[b]Crouch[/b]  Ctrl  ·  B
[b]Lean[/b]  Z and C  ·  the bumpers
[b]Use, talk, throw[/b]  E or left click  ·  A
[b]Answer[/b]  1 to 4, or the arrows and E  ·  the pad and A
[b]Lock, unlock[/b]  R  ·  Y
[b]Cover the lantern[/b]  F or right click  ·  left trigger
[b]Put the lantern away, take it out[/b]  G  ·  left on the pad
[b]Hold your breath[/b]  Space  ·  right trigger
[b]Look back[/b]  Q  ·  right stick
[b]The ledger[/b]  L  ·  View
[b]The satchel[/b]  I  ·  down on the pad
[b]Pause[/b]  Esc  ·  Menu
[b]Fullscreen[/b]  F11"""


func build() -> void:
	heading.text = "How to Play"
	page_width = 360.0
	page.custom_minimum_size.x = px(360.0)
	add_text(TEXT, 13.0)
	add_button("Back", func() -> void: back.emit())
