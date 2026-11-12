class_name GameFlow
extends Node
## The game from the title screen to the last chronicle (docs/log/full-game-run.md,
## "Done when" 1): New Game plays the chapters in order (night 0, day 1,
## nights 1 to 6), each opened by its chapter card, and when night 6 ends the
## ending's chronicle closes the game and chapter select opens. Continue
## picks up at the last bell. Esc or Start pauses (PauseMenu). Death is the
## capture flow's (back to the latest save); the night's director tells this
## node when the night is over.
##
## A level loaded directly (tests, tools: main's `level` or --level) plays on
## its own: no title, no next chapter.

signal title_shown
signal chapter_started(index: int)
signal ended(ending: StringName)

enum Mode { TITLE, CARD, PLAYING, ENDING }

## Seconds a chapter card's page takes to fade into the dark.
const CARD_LEAVE := 0.6

@export var main: Node
@export var fade: ScreenFade
@export var chapters: ChapterList
## The layer the menus and cards draw on, above everything.
@export var menus: CanvasLayer

var mode := Mode.PLAYING
var title: TitleMenu
var pause: PauseMenu
var settings: SettingsMenu
var how_to_play: HowToPlay
var chapter_select: ChapterSelect
## For testing, in debug builds: any chapter from any of its beats.
var scene_select: SceneSelect
var card: ChapterCard
var chronicle: ChronicleView

var _director: NightDirector
## The page Settings or How to Play goes back to.
var _return_to: MenuPage


func _ready() -> void:
	add_to_group(&"game_flow")
	process_mode = Node.PROCESS_MODE_ALWAYS
	title = _page(TitleMenu.new()) as TitleMenu
	title.backdrop = Manuscript.NIGHT
	pause = _page(PauseMenu.new()) as PauseMenu
	settings = _page(SettingsMenu.new()) as SettingsMenu
	how_to_play = _page(HowToPlay.new()) as HowToPlay
	chapter_select = ChapterSelect.new()
	chapter_select.chapters = chapters
	chapter_select.backdrop = Manuscript.NIGHT
	_page(chapter_select)
	scene_select = SceneSelect.new()
	scene_select.chapters = chapters
	scene_select.backdrop = Manuscript.NIGHT
	_page(scene_select)
	scene_select.back.connect(func() -> void:
		scene_select.close()
		title.open())
	scene_select.picked.connect(start_at)
	card = ChapterCard.new()
	card.backdrop = Manuscript.NIGHT
	_page(card)
	chronicle = ChronicleView.new()
	chronicle.backdrop = Manuscript.NIGHT
	_page(chronicle)
	title.chosen.connect(_on_title)
	pause.chosen.connect(_on_pause)
	pause.back.connect(resume)
	settings.back.connect(_back_from)
	how_to_play.back.connect(_back_from)
	chapter_select.back.connect(func() -> void:
		chapter_select.close()
		title.open())
	chapter_select.picked.connect(select_chapter)
	main.level_loaded.connect(_on_level_loaded)
	_start.call_deferred()


func _page(p: MenuPage) -> MenuPage:
	menus.add_child(p)
	return p


func _start() -> void:
	if main.get(&"current_level") == null:
		show_title()
		# For testing: `-- --from=night0:Arrive` starts there (debug builds).
		for arg in OS.get_cmdline_user_args():
			if OS.is_debug_build() and arg.begins_with("--from="):
				var parts := arg.trim_prefix("--from=").split(":")
				var i := chapters.index_of(StringName(parts[0]))
				if i >= 0:
					start_at(i, StringName(parts[1]) if parts.size() > 1 else &"")


func show_title() -> void:
	mode = Mode.TITLE
	get_tree().paused = false
	_close_pages()
	main.call(&"unload_level")
	Talk.reset()
	GameState.seconds_per_hour = 0.0
	fade.color.a = 0.0
	_free_mouse()
	title.open()
	title_shown.emit()


func new_game() -> void:
	GameState.new_game()
	await start_chapter(0, true)


## Continue: the last bell's chapter, from that bell.
func continue_game() -> void:
	var i := GameState.saved_chapter()
	if i < 0 or not GameState.load_last_bell():
		return
	GameState.carried = true
	_close_pages()
	_load_chapter(i)


## Chapter select: the chapter with the state a typical playthrough would
## have reached (the night's own start state, NightDirector).
func select_chapter(i: int) -> void:
	GameState.new_game()
	await start_chapter(i, false)


## For testing (SceneSelect): chapter `i` from the beat named `beat`, with no
## card, as a fresh game. The beats before it are skipped, not played.
func start_at(i: int, beat: StringName) -> void:
	_close_pages()
	get_tree().paused = false
	main.call(&"unload_level")
	Talk.reset()
	GameState.new_game()
	GameState.begin_chapter(i, chapters.chapters[i].night)
	GameState.start_beat = beat
	fade.color.a = 1.0
	await get_tree().process_frame
	_load_chapter(i)
	_fade_in_if_left_dark.call()


## Shows the chapter's card, then plays it. `carried`: it follows the
## chapter before in this playthrough.
func start_chapter(i: int, carried: bool) -> void:
	_close_pages()
	mode = Mode.CARD
	get_tree().paused = false
	main.call(&"unload_level")
	Talk.reset()
	GameState.begin_chapter(i, chapters.chapters[i].night)
	GameState.carried = carried
	await card.show_chapter(chapters.chapters[i])
	# The page fades into the dark, the chapter loads under black, and its
	# first beat fades the world in (if it doesn't, this does).
	fade.color.a = 1.0
	await card.leave(CARD_LEAVE)
	await get_tree().process_frame
	_load_chapter(i)
	_fade_in_if_left_dark.call()


func _fade_in_if_left_dark() -> void:
	await get_tree().create_timer(1.5).timeout
	if mode == Mode.PLAYING and fade.color.a > 0.98:
		fade.fade_to(0.0, 2.0)


func _load_chapter(i: int) -> void:
	mode = Mode.PLAYING
	main.call(&"load_level", load(chapters.chapters[i].scene))
	_capture_mouse()
	chapter_started.emit(i)


func _on_level_loaded(level: Node) -> void:
	if _director and is_instance_valid(_director) and _director.finished.is_connected(_on_night_finished):
		_director.finished.disconnect(_on_night_finished)
	_director = level.get_node_or_null(^"Director") as NightDirector
	if _director:
		_director.finished.connect(_on_night_finished)


func _on_night_finished() -> void:
	if GameState.chapter < 0 or mode != Mode.PLAYING:
		return
	var next := GameState.chapter + 1
	if GameState.has_flag(&"ending") or next >= chapters.chapters.size():
		await _ending()
	else:
		await start_chapter(next, true)


## The chronicle of how it ended, then the title, with chapter select open.
func _ending() -> void:
	mode = Mode.ENDING
	var id := StringName(GameState.get_flag(&"ending", Endings.DEFAULT))
	main.call(&"unload_level")
	Talk.reset()
	Settings.finished = true
	Settings.save_settings()
	# Nothing left to continue.
	for path in [GameState.save_path, GameState.quiet_path()]:
		if ResourceLoader.exists(path):
			DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	_free_mouse()
	await chronicle.show_ending(Endings.title(id), Endings.chronicle(id), Endings.last_line(id))
	ended.emit(id)
	show_title()


func open_pause() -> void:
	var flow := get_tree().get_first_node_in_group(&"capture_flow") as CaptureFlow
	if mode != Mode.PLAYING or get_tree().paused or (flow and flow.busy):
		return
	get_tree().paused = true
	_free_mouse()
	pause.open()


func resume() -> void:
	_close_pages()
	get_tree().paused = false
	_capture_mouse()


func _unhandled_input(event: InputEvent) -> void:
	if not Press.fresh(event, &"pause"):
		return
	if mode == Mode.PLAYING and not get_tree().paused:
		open_pause()
		get_viewport().set_input_as_handled()
	elif pause.visible:
		resume()
		get_viewport().set_input_as_handled()


func _on_title(what: StringName) -> void:
	match what:
		&"new_game":
			new_game()
		&"continue":
			continue_game()
		&"chapters":
			title.close()
			chapter_select.open()
		&"test":
			title.close()
			scene_select.open()
		&"how_to_play":
			_open_from(how_to_play, title)
		&"settings":
			_open_from(settings, title)
		&"quit":
			get_tree().quit()


func _on_pause(what: StringName) -> void:
	match what:
		&"resume":
			resume()
		&"settings":
			_open_from(settings, pause)
		&"how_to_play":
			_open_from(how_to_play, pause)
		&"quit_to_title":
			show_title()


func _open_from(p: MenuPage, from: MenuPage) -> void:
	_return_to = from
	from.close()
	p.open()


func _back_from() -> void:
	settings.close()
	how_to_play.close()
	if _return_to:
		_return_to.open()


func _close_pages() -> void:
	for p in [title, pause, settings, how_to_play, chapter_select, scene_select]:
		(p as MenuPage).close()


func _free_mouse() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE


func _capture_mouse() -> void:
	if DisplayServer.get_name() != "headless":
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
