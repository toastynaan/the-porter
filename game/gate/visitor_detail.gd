class_name VisitorDetail
extends Resource
## One thing the porter can notice about a visitor through the grille (design
## doc, "Knocks": read the visitor's boots, hands, story, what they carry).

## Where on him it is: "face", "body", "hands", "feet", "box" or "bag" (a
## marker of that name on the visitor).
@export var part := &"body"
## What the porter thinks, shown when he looks at it.
@export var line := ""
## The words that go into his ledger entry, if the porter noticed it.
@export var ledger := ""
## What it gives away, if it contradicts their story (docs/mechanics.md,
## "Lies"): "no pilgrim's badge". Noticing it, the porter thinks "(Something
## doesn't fit: no pilgrim's badge.)" and notes it.
@export var lie := ""
