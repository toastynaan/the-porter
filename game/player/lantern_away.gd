class_name LanternAway
extends Area3D
## A place where the porter keeps his lantern put away (docs/systems/mechanics.md,
## "Your hands"): indoors where others keep the light, as at the Cross Keys,
## where Hob's fire and candles light the rooms and nobody carries a flame
## among the straw and the drink. While he's inside, his lantern is put away
## and G does nothing; as he leaves it comes out again if it was out when
## he came in. Size it with its CollisionShape3D child.


func _ready() -> void:
	collision_layer = 0
	collision_mask = Layers.CAPSULE
	monitorable = false
	body_entered.connect(_entered)
	body_exited.connect(_exited)


func _entered(body: Node3D) -> void:
	if body is Player:
		(body as Player).lantern_hand.put_away_for(self)


func _exited(body: Node3D) -> void:
	if body is Player:
		(body as Player).lantern_hand.release(self)
