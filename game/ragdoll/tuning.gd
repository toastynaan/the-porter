class_name Tuning
## Gameplay numbers. The ragdoll block keeps big-kick's names and values, since
## game/ragdoll was tuned against them (and at 120 physics ticks per second).

# --- Ragdoll (ported from big-kick's Tuning) -----------------------------------
const WALK_SPEED := 4.5          ## m/s; the stagger push's step cycle is scaled to it
const GRAVITY := 20.0            ## m/s^2 on a staggering capsule (ragdolls use project gravity)
const AIR_RECOVERY_AFTER := 0.4
const GROUNDED_SPEED := 0.5      ## m/s pelvis speed
const GROUNDED_HOLD := 0.4       ## s under that speed
const GROUNDED_TIMEOUT := 3.0    ## s after first landing, whatever the speed
const GETUP_BLEND := 0.3         ## ragdoll -> get-up blend
const ACTIVE_RAGDOLL_MAX := 4    ## bodies running active muscles at once; the rest go passive
const DEAD_FREEZE_AFTER := 4.0   ## s at rest before a dead body freezes
const LOOSE_LIMB_MAX := 12
const PLAYER_GETUP_AFTER := 0.8  ## s on the ground for a host in the "player" group

## Partial and full ragdoll reactions (RagdollController.flinch / stumble /
## stagger / knockdown / launch). "physics" is the chain's physics share,
## "fade" the s it takes to fade back, "ground" the s range before a get-up.
const REACT_FLINCH := {"physics": 0.6, "fade": 0.25, "act": 0.3}
const REACT_STUMBLE := {"physics": 0.5, "hold": 0.3, "act": 0.6, "steps": Vector2(2, 3)}
const REACT_STAGGER := {"physics": 0.8, "fade": 0.6, "act": 0.8, "push": Vector2(0.6, 1.0)}
const REACT_KNOCKDOWN := {"ground": Vector2(1.2, 2.0)}
const REACT_LAUNCH := {"ground": Vector2(1.5, 2.5)}
const HITSTOP_JITTER_RANGE := Vector2(0.02, 0.04)  ## m victim mesh jitter during the freeze
const LAUNCH_SPEED_MIN := 6.0
const LAUNCH_SPEED_MAX := 18.0   ## cap on every flying body

static var debug_clip_anims := false     ## big-kick's Mixamo clips (not shipped here)
static var debug_sketch_strikes := true  ## big-kick's strike variants; unused by zombies

# --- Zombies ---------------------------------------------------------------------
const ZOMBIE_HEALTH := 100.0
const ZOMBIE_MASS := 70.0        ## kg; bone masses scale from it
const ZOMBIE_SPEED := 1.1        ## m/s shamble
const ZOMBIE_TURN_SPEED := 2.5   ## rad/s
const ZOMBIE_SIGHT := 30.0       ## m: farther than this from the player it stands still
const ZOMBIE_STOP_DIST := 0.95   ## m from the player (capsule centres) it stops at

# --- Player melee --------------------------------------------------------------------
const PUNCH_REACH := 1.4         ## m from the eye
const PUNCH_SPREAD := 0.15       ## m: the four side rays run this far off the centre ray
const PUNCH_DAMAGE := 20.0
const PUNCH_HEAD_MULT := 1.5
## A third hit within this many seconds of the first staggers instead of flinching.
const PUNCH_COMBO_WINDOW := 1.2
const PUNCH_STAGGER_HITS := 3
## Hitstop (real s) on the zombie and the arms, by reaction.
const PUNCH_HITSTOP := {&"flinch": 0.05, &"stumble": 0.06, &"stagger": 0.07, &"knockdown": 0.09, &"kill": 0.12}
## m/s a killing blow throws the body (along the punch, plus up).
const PUNCH_KILL_PUSH := Vector2(4.0, 1.2)
