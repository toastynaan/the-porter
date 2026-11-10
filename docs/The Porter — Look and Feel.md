# The Porter — Look and Feel

Nov 6, 2026 · @Pahul

**Changes, Nov 8 2026:** an almost-no HUD (thin outlines on usable things, a faint marker over what the current duty needs); how deaths are shown; the Hungry Saint's look on night 6; the Cross Keys inn, drunkenness, daytime and the squints for the night-0 prologue. See `docs/full-game-run.md`.

## Direction

**Candlelit lo-fi realism.** Real medieval materials and proportions, rendered at low fidelity, in near-total darkness, lit almost only by what the characters carry. The player should always be able to see a little less than they want to.

This direction is also practical. A low-resolution, dark, grainy look hides the mismatch between models you make in Blender and assets you find elsewhere, keeps texture work cheap, and lets the player's imagination do the scary part.

**Three rules**

1. **Darkness is the default.** Anything not lit by a flame or the moon is close to black.
2. **Real things, low detail.** Correct shapes and materials (stone, wood, wool, wax), simple geometry, low-resolution textures.
3. **Two looks.** Sober is cold, flat and plain. Drugged is warm, soft and wrong. The player should feel the difference before they understand it.

**References**

| Reference | Take from it |
| --- | --- |
| *The Witch* (2015 film) | Candle and window light only; muted, cold daylight; period clothing that looks worn |
| *The Name of the Rose* (1986 film) | The abbey itself: stone, crowded scriptorium, monks as a mass of identical habits |
| *Amnesia: The Dark Descent* | Darkness as a resource; the lantern as your lifeline |
| *Slender: The Eight Pages* | How to stage the demon in the Glimpses phase: far, still, gone |
| *Fears to Fathom* | Lo-fi realism, mundane tasks, NPCs that feel like people |
| *Pentiment* | Medieval manuscript look for the ledger, notes and chronicle epilogues |

## Rendering style

Slightly degraded, not retro. The image should feel like an old memory, not a PS1 game: no wobbling vertices, no warped textures, nothing that reads as a joke.

| Element | Spec | Why |
| --- | --- | --- |
| 3D resolution | Render at half resolution (960×540 on a 1080p screen), upscale with nearest-neighbour | Softens detail and hides mismatched assets; text and UI stay full resolution |
| Textures | 512×512 for most props, 1024×1024 for walls, floors and hero props; no 4K | Low detail, consistent across made and found assets |
| Film grain | Light and always on; stronger in the dark | Fills black areas so the dark feels alive, not empty |
| Dithering | Ordered dither on dark gradients | Removes colour banding in near-black and gives a hand-made texture |
| Vignette | Medium, darker at higher Dose | Pulls focus to the centre and the lantern |
| Depth of field | None while sober; soft blur at Dose 50+ | Sober is sharp and plain; drugged is soft |
| Colour depth | Slight posterise (about 48 levels per channel) | Gives a printed, aged look without looking retro |

## Colour palette

Most of the screen is near-black, stone grey and moonlight blue; the only warm colour is flame. Red appears only in blood and, when drugged, the demon's eyes.

**Sober palette**

| Name | Hex | Use |
| --- | --- | --- |
| Night | #0B0C10 | Shadows, which is most of the screen |
| Black habit | #1E1B19 | Monks' robes; Benedictines wore black |
| Stone | #5A5A57 | Walls, floors, tombs |
| Moonlight | #6E7F96 | Outdoor fill light, windows, fog |
| Lantern | #E0A458 | Every flame: lantern, candles, rushlights |
| Parchment | #D8C9A3 | Ledger, wax, bone, faces in lantern light |
| Old blood | #5A1A14 | Blood, always dark and dry-looking, never bright |

**Drugged shift (scales with Dose)**

| Change | Target | Notes |
| --- | --- | --- |
| Shadows lift and warm | #2A1622 (bruise purple) | Black stops being black; the dark looks like it is breathing |
| Highlights go sickly | #B8B04A (ergot yellow-green) | Flames and skin pick up an ill tint |
| Saturation | +30% on reds and ambers only | Blood and fire get louder; everything else stays dull |
| Demon eyes | #FF5A1F (ember) | Only colour that is fully saturated anywhere in the game |

The sober image should look slightly too plain, almost a relief, so that the drugged shift is felt rather than noticed.

## Lighting rules

Light is the player's resource and the cult's weapon. Every light source in the game is a flame or the moon.

1. **The lantern is the main light.** Warm, about 5 m of useful reach, with a slow flicker. It gutters in wind, near open doors and at high Dose. Covering it drops reach to about 1 m.
2. **Moonlight is fill, not sight.** Cold, low, through windows and cloister arches. It shows shapes and silhouettes, never detail. The demon is always staged against moonlight.
3. **Candles mark people.** A lit window or a candle on a table means someone is there or was just there. Lights that go out are events.
4. **Faces lit from below.** NPCs at night are lit by the lantern you hold or the candle they carry. Kind faces still look wrong.
5. **Silhouettes beat detail.** Anything scary is shown first as a dark shape against a lighter background, never fully lit.
6. **Day scenes are flat and grey.** Supper and dawn use overcast window light with no strong shadows. Daylight should feel safe and slightly dead.
7. **Fog carries light.** On fog nights the lantern becomes a glowing ball that shows where you are to anyone watching.

## Camera and player feel

First person, with a body. You are a 19-year-old monk in a heavy wool habit, not a soldier.

| Element | Spec |
| --- | --- |
| Field of view | 70° default, adjustable 60–90°; narrows by about 5° while staring at the demon |
| Walk | Slow, about 1.4 m/s, with gentle head bob and the habit's hem visible when looking down |
| Run | About 4 m/s; heavier bob, lantern swings and throws shadows around |
| Lantern | Held low in the left hand, always in view. Its swing is the main motion on screen |
| Hands | Visible for every interaction: barring the gate, writing the ledger, pulling the bell rope |
| Hunger | Hand tremor on the lantern; slower to get back to full sprint |
| Hiding | Camera drops low, view framed by whatever you hide in; breathing gets loud |
| Looking back | Hold a key to look over your shoulder while running, as in *Outlast* |

Weight matters more than speed. Doors are heavy and take a moment to open, the gate bar takes two hands, and the bell rope pulls you up off your feet.

## The demon's look

The demon must read as a silhouette from 30 m away in moonlight: too tall, too thin, crowned with horns, no visible feet. It is one model with three render states, so the drugged version is always built on top of the real costume.

**The costume (the real thing)**

| Part | Design | Detail a sober player can spot |
| --- | --- | --- |
| Headdress | Stag antlers lashed to ram's horns on a leather cap; adds about 60 cm | Leather ties and a rope knot at the back of the head |
| Mask | Pale carved wood, long face, eye holes, no mouth | Tool marks, a crack, human eyes moving behind it |
| Cloak | Black habit with a long hood, hem dragging on the ground so the feet never show | Patches, mud on the hem, boots showing when it runs |
| Hands | Carved wooden finger extensions over gloves | The joins at the knuckles |
| Feet | Felt overshoes, or carved hoof soles when they want to be heard | The hoof soles are strapped to ordinary boots |

**Three costumes, one difference.** All three look identical at a distance, but Ranulf's has one broken antler. On night 4, when two appear at once, a sharp player sees one with both antlers intact.

**Render states by Dose**

| Dose | How the demon renders |
| --- | --- |
| 0–49 | The costume as it is: a tall man in a mask. Only reachable from night 4, when incense can be avoided |
| 50–74 | About 15% taller, eyes glow ember (#FF5A1F), mask and hood merge into one dark shape, fingers longer |
| 75–100 | Limbs stretched, antlers slowly branching, breath visible as smoke, the mask's face shifting when you aren't looking straight at it |

Build it as one rigged model with blend shapes for the stretched limbs and face, plus an emissive eye material driven by Dose. Avoid a separate "monster" model: the player should never see a pop between versions, only drift.

## Characters

Every brother wears the same black habit, which is accurate and good for the horror (the headcount, the hooded strangers). It also means each NPC must be recognisable in the dark by four things: **build, face, one prop, one sound.**

| Character | Build | Face | Prop | Sound |
| --- | --- | --- | --- | --- |
| Brother Thomas | Tall, thin, stooped | Gentle, deep-set eyes | Herb pouch, stained fingers | Mortar and pestle; a hum |
| Brother Osric | Short and heavy | Round, red, always smiling | Big ring of cellar keys | Keys jingling |
| Brother Ranulf | Average, rigid posture | Narrow, pale, unblinking | Censer for the incense | Censer chain clinking |
| Cole and Dunstan | Big labourers | Weathered, blank | Brown work tunics, not habits | Heavy boots, no talk |
| Abbot Godric | Small, frail | Very old, kind | Crosier he leans on | Coughing from the incense |
| Prior Hugh | Lean, upright | Hard, scarred jaw | Wax tablet he writes notes on | Quick, sharp footsteps |
| Brother Anselm | Hunched in a chair | Milky blind eyes | Walking stick | Stick tapping on stone |
| Brother Edwin | Young, gangly | Freckled, nervous grin | Always carrying a book | Talks too fast |
| Mab | Small, wrapped in rags | Face covered by cloth | A leper's clapper, as lepers carried to warn people | The clapper |
| Walter the pardoner | Plump | Oily, cheerful | Coloured cloak, box of "relics" | Rattling relic box |
| Joan | Slight, travel-worn | Sharp, watchful | Her brother's pilgrim badge | Rarely speaks first |
| Pilgrims | Varied | Varied | Staff, shoulder bag, pilgrim badges on hats | Varied |

**Build approach:** one base body mesh for all brothers in the habit, with head swaps, a few body-shape blend shapes (thin, heavy, hunched) and attached props. Pilgrims use the same base with different clothing pieces. Walter is the only saturated colour on any character.

## Drink and daylight

- **Drunk** (night 0) isn't drugged. It's a warm smear and a slow double image that drifts with the view, with no palette shift and no bruise purple, so the player never mistakes ale for the abbey's drug. Day 1 starts with a faint headache blur until noon.
- **Day 1** is the only full daylight: overcast, flat and grey, no strong shadows (lighting rule 6). The abbey by day looks plain and harmless, which is the point.

## Deaths

People die in front of the player, and how much is shown varies on purpose, so no death can be braced for:

| Style | What's on screen | Used for |
| --- | --- | --- |
| Implied | A shape against the light, a struggle half-seen, a cry cut off, a lantern dropped and rolling. Then the body, or only the blood | Deaths in the fog, in the dark, far off |
| Gory | The wounds in view, blood up the wall, the body left as it fell | The guesthouse, the crypt, night 6 |
| The throat | One quick cut and blood flying through the lantern light | The lane, the dilemma, Cole at the gate |

- Blood stays dark even fresh: old blood (#5A1A14), never bright. It's the one red that isn't flame or the demon's eyes.
- Drugged, the killer is the demon (long fingers, a crown of horns); sober, a man in a mask.
- The body falls (a ragdoll) and stays until the cult moves it. Blood stays until they scrub it.

## The Hungry Saint (night 6)

The real demon is not the costume. It must never look like a man in a mask, so a sober player knows the difference at once.

- **Shape:** taller than the costume, about 2.6 m, and too thin, bent forward under the vaults. No horns: the antlers were the cult's idea of it.
- **Light:** your lantern dims as it nears, and candles gutter toward it. It is lit by nothing; you see it as a gap in the light.
- **Movement:** slow and in view, unlike the costume. It moves only on the ground, never quickly.
- **Sound:** silence before it. Rooks, rats, the cat and the wind all stop.
- **Dose:** it looks the same drugged or sober. That is how the player knows it's real.
- **Seen once before:** on night 0, sober, through a squint in the abbey wall: too tall, too thin, no horns, gone when you look again. On night 6 the player should recognise it.

## Environments and materials

The abbey is plain, worn and cramped. It's a working building, not a cathedral: low ceilings, narrow doors, thick walls, small windows.

**Materials (keep to this list)**

| Material | Where | Look |
| --- | --- | --- |
| Rough limestone blocks | Walls, cloister arches | Grey, soot-stained above head height |
| Worn flagstones | Floors, cloister walk | Uneven, dipped where feet have walked for centuries |
| Dark oak | Doors, beams, choir stalls | Nearly black with age, iron studs and hinges |
| Lime plaster | Dormitory, infirmary | Off-white, cracked, damp patches |
| Wool and linen | Bedding, habits, curtains | Heavy, dull, frayed |
| Beeswax and tallow | Candles everywhere | Drips that build up on surfaces; drips are a clue system |
| Earth and mud | Graveyard, outer court, the lane | Wet, footprints persist |
| Cobbles | The lane outside the gate, with a gutter down the middle | Uneven, wet, reflecting the lanterns |
| Bone | Charnel house, crypt | Stacked neatly, which is worse than scattered |

**The lane outside the gate**

The city presses against the abbey's west wall. The lane is narrow and tall: timber-framed houses of three or four storeys, lime plaster between dark oak, each upper floor jutting out over the one below, gable ends to the street. Lanterns hang from iron brackets outside the houses, so the lane is a row of warm pools in fog; lit windows show who is awake. The inn stands opposite the gate. The view up the lane ends on a great church front in the fog. Beyond the roofs: more roofs, spires, the city wall.

Mood references (street and gate images, Nov 2026): rain-wet streets with lamp pools and fog, tall facades closing in, a Gothic church at the end of the lane, an ivy-grown stone gate arch with a lantern and a lodge beside it. Take the mood, not the period details: no lamp posts, iron balconies, sash windows or ornamental ironwork. The medieval versions are lanterns on brackets, jettied upper floors, small shuttered or horn-paned windows, and a plain barred grille.

**The Cross Keys** is the warmest room in the game, and it's meant to be: low beams, a big hearth, tallow smoke, faces lit orange, noise. It's the last warm place before the abbey, so the player feels its loss. Its upper rooms are small and cold, with one window toward the abbey.

**The lane by the hour.** At dusk it's busy and lit: doors open, people going home, the inn loud. At nine the curfew bell rings and it empties. After that there are only the lanterns, the watchman's light moving between them, and lit windows going dark one by one, until it's as dark as the abbey.

**The squints** are three small barred windows in the abbey wall, about a hand's width by a forearm's height, at eye level. From outside they show slivers of the court; from inside, slivers of the lane.

**The road in (night 0).** The wagon ride is grey dusk over mud and ruts: the white chapel in the fields, then the city wall and Aldgate's dark arch, then the close, tall streets. It's the only time the player sees beyond the lane.

**Dressing rules**

- Every room should look in use: a half-finished meal, a book left open, a habit on a peg. Lived-in spaces make empty ones scarier.
- Religious imagery is everywhere: carved saints, painted crosses, wall paintings of the Last Judgement. When drugged, these are what move first.
- Keep sightlines short indoors and long outdoors. The cloister is the exception: one long view down each walk, interrupted by pillars.
- Decay increases across nights: more dripped wax, more unlit candles, doors left open, stains that aren't cleaned.

## UI

Almost no HUD. Everything the player needs to know is in the world or in an object they hold, with two quiet exceptions so a first-time player is never lost: an outline on what you can use, and a faint mark over what your duty needs. Neither may take away from the dark.

| Need | Shown by |
| --- | --- |
| Time and next duty | Candle clock in your cell; church bells; the moon's position |
| Who came in | The ledger, written in a manuscript hand on parchment |
| Health and hunger | Hand tremor, breathing, slower sprint recovery |
| Dose | Never shown directly; only through the image itself |
| Suspicion | Never shown; NPC behaviour changes instead |
| Interact prompt | A small dot in the centre. What E would use gets a thin, pale outline while you look at it, within reach |
| Objectives | The candle-clock marks and the ledger say what's due. A small, dim glyph floats over the one person or thing the current duty needs, seen within about 10 m, and never during a chase or while hiding (a setting turns it off). The lit way to each duty stays |
| Dialogue | Plain subtitles at the bottom in the book typeface, speaker name in small caps (lantern-coloured), no portraits. Up to three numbered answers under the line, left-aligned, then "Walk away"; the chosen one brighter, with a thin flame-coloured bar. A soft dark gradient under them, no box (`docs/dialogue.md`, "How it looks") |

**Menus and text** use the manuscript style: parchment background, blackletter only for titles, a readable book typeface for everything else. Chapter cards for each night look like a page from the chronicle, with a decorated initial letter. Keep blackletter out of body text; it is hard to read.

## Sound feel

No music in the usual sense. The score is the abbey: chant, bells, wind and people.

- **Chant is the theme.** Plainchant at Matins is the only real music. Its melody returns everywhere: hummed by Thomas, hummed by hunters on their rounds, whispered backwards at high Dose.
- **Bells are the clock.** The city's church bells and the abbey bell mark time. A bell at the wrong hour is a scare.
- **The room tone is never silent.** Wind under doors, the mill wheel, rats, a snore from the dorm, a cough. Then the demon comes and it all goes quiet.
- **Footsteps tell you who.** Every surface has its own sound (stone, wood, mud, straw), and each NPC has a step rhythm. Hoof soles on stone are the loudest sound in the game.
- **Your body is loud.** Breathing, heartbeat when hiding, the lantern's creak, the habit dragging. Holding your breath cuts all of it.
- **Drugged audio** (Dose 25+): reverb grows, whispers sit just below hearing, sounds come from the wrong direction, your name is called in Edwin's voice after he dies.
- **Silence is the scariest sound.** Use full silence rarely: at most once per night.

## Asset pipeline

Make the hero assets in Blender: the demon, the brothers' base body, the abbey's modular kit and key props. Source the filler (textures, furniture, clutter, generic animations), then run everything through the same finishing pass so made and found assets match.

**Blender conventions**

- Metric units, 1 Blender unit = 1 m. Apply rotation and scale before export.
- Export glTF 2.0 binary (.glb) for everything, including found assets you have cleaned up. The glTF exporter handles Blender's Z-up to Godot's Y-up.
- Modular abbey kit on a 1 m grid: wall pieces 4 m wide by 4 m tall, arch pieces matching, so rooms snap together and the map stays easy to change.
- Naming: `env_` for kit pieces, `prop_` for props, `chr_` for characters, `tex_` for textures. Collision meshes use Godot's import suffixes (such as `-colonly`) so collision comes in automatically.
- Texel density about 256 px per metre for environment surfaces, which matches 1024 textures on 4 m wall pieces.

**Budgets**

| Asset type | Triangles | Texture |
| --- | --- | --- |
| Small prop (cup, candle, book) | 50–500 | Shared atlas or 256–512 |
| Furniture (bed, table, choir stall) | 500–3,000 | 512 |
| Modular wall or arch piece | 200–2,000 | Shared tiling 1024 |
| NPC in habit | 4,000–8,000 | 1024 body, 512 head |
| The demon | Up to 10,000 | 1024, plus emissive eyes |

**Where to find assets**

| Source | What for | Licence |
| --- | --- | --- |
| [Poly Haven](https://polyhaven.com/license) | Stone, wood and plaster textures; some props | CC0: any use, no credit needed |
| [ambientCG](https://ambientcg.com) | Largest free PBR material library | CC0, commercial use allowed |
| [Quaternius](https://quaternius.com) | Animation library for prototyping | CC0 |
| [Mixamo](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html) | Walk, run, idle, sit and pray animations | Royalty-free in commercial games; raw files can't be redistributed |
| [Fab](https://www.fab.com/eula) | Paid or free medieval props and kits | Standard licence assets can be used outside Unreal; Reference Only, legacy Quixel and Epic sample content cannot. Check each listing |
| Sketchfab and itch.io | One-off props | Varies per asset: CC-BY needs credit, NonCommercial can't ship in a paid game |

Poly Haven and ambientCG textures are photoscanned at high resolution; downscale them to the budgets above.

**Finishing pass (every asset, made or found)**

1. Check real-world scale against a 1.75 m reference person.
2. Decimate to the triangle budget.
3. Downscale textures to 512 or 1024 and pull colours toward the palette (desaturate, cool the greys).
4. Add the shared grime layer: soot from above, damp from below, wear on edges.
5. Log it in a credits sheet: asset, source link, author, licence, credit required.

Mixamo animations go onto your own rigs through Godot 4's humanoid retargeting, so one set of clips can drive every NPC.

## Godot 4 render setup

One post-process shader and one Dose value drive the whole look.

| Setting | Choice | Notes |
| --- | --- | --- |
| Renderer | Forward+ | Needed for volumetric fog |
| Half-resolution look | Render the 3D world into a SubViewport at 960×540, show it on a full-screen TextureRect with nearest filtering | Godot's built-in 3D scaling modes smooth the image; the SubViewport route gives the crisp low-res look. UI draws on top at full resolution |
| Post-process | One canvas shader on that TextureRect: grain, ordered dither, posterise, vignette, palette shift, edge warp | All driven by a `dose` uniform from the game-state autoload |
| Tonemap | Filmic, low exposure | Keep blacks crushed |
| Ambient light | Near-black, slightly blue | Darkness is the default |
| Volumetric fog | On, low density; high density on the fog night | Lantern and moonlight set to cast into the fog |
| Moonlight | DirectionalLight3D, cold and dim; static bounce baked with LightmapGI | Baking is cheap and keeps the dark consistent |
| Lantern | OmniLight3D, about 5 m range, shadows on, flicker script | The most important light in the game |
| Candles | OmniLight3D, small range, shadows off except hero candles | Cap at about 4 shadow-casting lights on screen |
| Glow | On, low, flames only | Makes fire read as the only warm thing |
| SSAO | On | Grounds the low-detail geometry |
| SDFGI | Off | Too costly, and it lifts the darkness |

**Dose drives** the post shader's warp, colour shift and blur, the Environment's saturation and fog colour, the demon's render state, and audio reverb. Tween it so changes are slow; the player should never see a step.

## Sources

- [Poly Haven licence](https://polyhaven.com/license) and [home page](https://polyhaven.com/) (CC0)
- [ambientCG](https://ambientcg.com) (CC0, commercial use allowed)
- [Mixamo FAQ, Adobe](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html) and [Adobe community licensing thread](https://community.adobe.com/t5/mixamo-discussions/mixamo-faq-licensing-royalties-ownership-eula-and-tos/td-p/13234775)
- [Fab EULA](https://www.fab.com/eula) and [Unreal forum thread on using Fab assets in other engines](https://forums.unrealengine.com/t/ability-to-use-purchased-items-outside-of-unreal-engine/2370367/2)
- [Free animation and rigging guide (Quaternius CC0)](https://app.cinevva.com/guides/free-character-animations-rigging)
