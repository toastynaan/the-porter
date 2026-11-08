class_name Rumours
## What the lane says at dusk about the night before (docs/full-game-run.md,
## "The lane": the rumours run ahead of you; docs/mechanics.md, "Saving
## people": the lane's talk at the next dusk tells him what would have saved
## them). Each rumour is a line for someone in the lane, said when its flags
## hold; the lane's dusk conversations (M12) carry them. DRAFT lines.

## [who, line, flags that must hold ("flag" or "flag=value"), flags that mustn't]
const ALL := [
	[&"hob", "That merchant who went in at your gate. They say he was pulled out of the fishpond this morning. The old porter used to lock his guests in at night, you know. Nobody does now.",
		["died_merchant"], []],
	[&"hob", "Your merchant came by at first light, hale, cursing your porter for locking him in like a sheep. Paid for his ale, at least.",
		["n1_merchant=admitted", "n1_guesthouse_locked"], ["died_merchant"]],
	[&"agnes", "The merchant you turned away slept upstairs here. Grumbled all night. Better grumbling than in that place.",
		["n1_merchant_fate=cross_keys"], []],
	[&"agnes", "Turned away after the bell, poor soul, and the Keys was shut. They found him in the gutter. Send them to us before nine, brother.",
		["died_lane_death", "lane_death_was_turned_away"], []],
	[&"hob", "I put Jankin out at closing, same as every night. He's dead in the gutter. I should have kept him in.",
		["died_jankin"], []],
	[&"hob", "Kept Jankin in, like you asked. Snored on my bench till dawn. Something walked the lane last night. I heard it.",
		["n2_jankin_kept_in"], ["died_jankin"]],
	[&"agnes", "They say the guesthouse door was locked, and it made no difference. Whoever goes in there has keys. If a guest of yours must stay, tell him to bar it from inside.",
		["died_night4_guest"], []],
	[&"agnes", "Your guest last night barred his own door, he says, and sat up with a knife till dawn. He's gone home to Kent and won't be back.",
		["n4_warned_night4_guest"], ["died_night4_guest"]],
	[&"hob", "The bailiff's man who stood at your gate all night. They found his lantern out and him in the lane. Why didn't you let him in, brother?",
		["died_sergeant"], []],
]


## The lines the lane says tonight, about the night before: [who, line].
static func tonight() -> Array:
	var out := []
	for r: Array in ALL:
		if _all(r[2], true) and _all(r[3], false):
			out.append([r[0], r[1]])
	return out


static func _all(flags: Array, want: bool) -> bool:
	for f: String in flags:
		var holds: bool
		if "=" in f:
			var parts := f.split("=")
			holds = str(GameState.get_flag(StringName(parts[0]), "")) == parts[1]
		else:
			var v: Variant = GameState.get_flag(StringName(f), false)
			holds = v != null and not (typeof(v) == TYPE_BOOL and not v)
		if holds != want:
			return false
	return true
