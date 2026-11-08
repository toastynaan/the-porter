class_name Wine
## Thomas's wine on night 6 (design doc, "Sources": +40 on cult kill nights;
## refusing Thomas directly is a large Suspicion jump). Drunk, the porter is
## the cult's for the taking: caught on night 6 after it, he wakes in a habit
## (the New Faith ending).

const DOSE := 40.0
const DOSE_TIME := 20.0
const REFUSED := 20


static func drink() -> void:
	GameState.add_dose(DOSE, DOSE_TIME)
	GameState.set_flag(&"drank_wine")


static func refuse() -> void:
	GameState.raise_suspicion(REFUSED)
	GameState.set_flag(&"refused_wine")
