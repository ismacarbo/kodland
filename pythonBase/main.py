# main_final.py — PgZero roguelike (menu, audio, slider volume, nemici, HP, animazioni)
# -------------------------------------------------------------------------------------
# Librerie consentite: PgZero, math, random (+ Rect da pygame)
# Asset richiesti:
#   images/hero_idle_0..3.png, images/hero_walk_0..3.png
#   images/slime_idle_0..2.png, images/slime_walk_0..3.png
#   sounds/step.ogg, sounds/hit.ogg, sounds/click.ogg
#   music/theme.ogg
#
# Avvio:
#   pgzrun main_final.py

from pygame import Rect
from math import hypot
from random import choice, randint

# --- Config griglia ---
TITLE = "Roguelike su griglia con PgZero"
TILE = 64
COLS, ROWS = 10, 8
WIDTH, HEIGHT = COLS * TILE, ROWS * TILE

# --- Stati gioco ---
STATE_MENU = "menu"
STATE_GAME = "game"
state = STATE_MENU

# --- Audio flags e volume ---
music_enabled = True
sfx_enabled = True
master_volume = 0.8  # 0.0..1.0

# --- Layout Menu (sposta i bottoni più in giù) ---
MENU_TITLE_Y = 80
MENU_INFO_Y = 130
SLIDER_Y = 200
SLIDER_W = 360
SLIDER_H = 8
BUTTON_W, BUTTON_H, BUTTON_GAP = 300, 64, 16
BUTTONS_BASE_Y = 280  # <- più in basso per lasciare spazio a titolo + info + slider

# Slider state
dragging_slider = False

# --- Mappa semplice (# = muro, . = pavimento) ---
LEVEL = [
    "##########",
    "#........#",
    "#..##....#",
    "#........#",
    "#...##...#",
    "#........#",
    "#..#.....#",
    "##########",
]


def grid_to_px(gx, gy):
    return gx * TILE + TILE // 2, gy * TILE + TILE // 2


def is_blocked(gx, gy):
    if gx < 0 or gy < 0 or gx >= COLS or gy >= ROWS:
        return True
    return LEVEL[gy][gx] == "#"


def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def set_master_volume(v):
    """Aggiorna il volume di musica e SFX (0..1)."""
    global master_volume
    master_volume = clamp(v, 0.0, 1.0)
    try:
        # Musica
        music.set_volume(master_volume)
    except Exception:
        pass
    # SFX: settiamo di volta in volta prima di play() in play_sfx()


def play_sfx(name):
    if not sfx_enabled:
        return
    try:
        s = getattr(sounds, name)
        # Imposta il volume ogni volta per essere sicuri che rispetti lo slider
        try:
            s.set_volume(master_volume)
        except Exception:
            pass
        s.play()
    except Exception:
        pass


class AnimatedActor:
    """Attore su griglia con animazione idle/walk e interpolazione."""

    def __init__(self, idle_frames, walk_frames, gx, gy, speed=220):
        self.idle_frames = idle_frames or ["hero_idle_0"]
        self.walk_frames = walk_frames or self.idle_frames
        self.gx, self.gy = gx, gy
        self.x, self.y = grid_to_px(gx, gy)
        self.tx, self.ty = self.x, self.y
        self.speed = speed
        self.moving = False
        self.state = "idle"
        self.frame_index = 0
        try:
            self.actor = Actor(self.idle_frames[0], anchor=("center", "center"))
            self.actor.pos = (self.x, self.y)
        except Exception:
            self.actor = None

    # animazione
    def set_state(self, st):
        if self.state != st:
            self.state = st
            self.frame_index = 0

    def step_animation(self):
        frames = self.walk_frames if self.moving else self.idle_frames
        if not frames:
            return
        if self.actor:
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.actor.image = frames[self.frame_index]

    # movimento
    def start_move_grid(self, dx, dy):
        if self.moving:
            return False
        nx, ny = self.gx + dx, self.gy + dy
        if is_blocked(nx, ny):
            return False
        self.gx, self.gy = nx, ny
        self.tx, self.ty = grid_to_px(nx, ny)
        self.moving = True
        self.set_state("walk")
        return True

    def update_motion(self, dt):
        if not self.moving:
            self.set_state("idle")
            return
        vx, vy = self.tx - self.x, self.ty - self.y
        dist = hypot(vx, vy)
        step = self.speed * dt
        if dist <= step:
            self.x, self.y = self.tx, self.ty
            self.moving = False
            self.set_state("idle")
        else:
            self.x += (vx / dist) * step
            self.y += (vy / dist) * step
        if self.actor:
            self.actor.pos = (self.x, self.y)

    def draw(self):
        if self.actor:
            self.actor.draw()
        else:
            screen.draw.filled_circle((self.x, self.y), 20, "white")
            screen.draw.circle((self.x, self.y), 20, "black")


class Player(AnimatedActor):
    def __init__(self, gx, gy):
        super().__init__(
            idle_frames=["hero_idle_0", "hero_idle_1", "hero_idle_2", "hero_idle_3"],
            walk_frames=["hero_walk_0", "hero_walk_1", "hero_walk_2", "hero_walk_3"],
            gx=gx,
            gy=gy,
            speed=260,
        )
        self.hp = 5
        self.invuln_timer = 0.0

    def update(self, dt):
        if self.invuln_timer > 0:
            self.invuln_timer -= dt
        self.update_motion(dt)

    def try_move(self, dx, dy):
        if self.start_move_grid(dx, dy):
            play_sfx("step")

    def take_hit(self, dmg=1):
        if self.invuln_timer > 0:
            return
        self.hp = max(0, self.hp - dmg)
        self.invuln_timer = 0.6
        play_sfx("hit")


class Enemy(AnimatedActor):
    def __init__(self, gx, gy):
        super().__init__(
            idle_frames=["slime_idle_0", "slime_idle_1", "slime_idle_2"],
            walk_frames=["slime_walk_0", "slime_walk_1", "slime_walk_2", "slime_walk_3"],
            gx=gx,
            gy=gy,
            speed=180,
        )
        self.decide_timer = 0.0

    def update(self, dt, player):
        self.decide_timer -= dt
        if not self.moving and self.decide_timer <= 0:
            self.decide_timer = 0.35 + randint(0, 20) * 0.01
            # 55% di inseguimento su un solo asse, 45% vagabondaggio
            if randint(0, 100) < 55:
                dx = 1 if player.gx > self.gx else -1 if player.gx < self.gx else 0
                dy = 1 if player.gy > self.gy else -1 if player.gy < self.gy else 0
                if dx != 0 and dy != 0:
                    if randint(0, 1) == 0:
                        dy = 0
                    else:
                        dx = 0
            else:
                dx, dy = choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            self.start_move_grid(dx, dy)
        self.update_motion(dt)


# --- Oggetti di gioco (creati su Start) ---
player = None
enemies = []

# --- Menu: bottoni ---
buttons = []


def build_buttons():
    center_x = WIDTH // 2
    labels = ["Avvia partita", "Attiva/Disattiva musica e suoni", "Esci"]
    out = []
    for i, label in enumerate(labels):
        r = Rect(0, 0, BUTTON_W, BUTTON_H)
        r.center = (center_x, BUTTONS_BASE_Y + i * (BUTTON_H + BUTTON_GAP))
        out.append({"rect": r, "label": label})
    return out



buttons = build_buttons()


def start_game():
    global state, player, enemies
    player = Player(1, 1)
    enemies = []
    while len(enemies) < 4:
        gx, gy = randint(1, COLS - 2), randint(1, ROWS - 2)
        if is_blocked(gx, gy) or (abs(gx - player.gx) + abs(gy - player.gy) < 4):
            continue
        enemies.append(Enemy(gx, gy))
    state = STATE_GAME
    # musica
    try:
        music.set_volume(master_volume)
        if music_enabled:
            music.play("theme")
        else:
            music.stop()
    except Exception:
        pass


def back_to_menu():
    global state
    state = STATE_MENU
    try:
        music.stop()
    except Exception:
        pass


# --- Disegno ---
def draw_grid():
    for gy in range(ROWS):
        for gx in range(COLS):
            x, y = gx * TILE, gy * TILE
            r = Rect(x, y, TILE, TILE)
            if LEVEL[gy][gx] == "#":
                screen.draw.filled_rect(r, (35, 40, 60))
            else:
                screen.draw.filled_rect(r, (24, 26, 36))
            screen.draw.rect(r, (15, 15, 22))


def draw_menu_slider():
    """Disegna lo slider del volume (bar + knob + etichette)."""
    bar_x = WIDTH // 2 - SLIDER_W // 2
    bar_y = SLIDER_Y
    bar_rect = Rect(bar_x, bar_y - SLIDER_H // 2, SLIDER_W, SLIDER_H)

    # barra
    screen.draw.filled_rect(bar_rect, (80, 82, 105))
    screen.draw.rect(bar_rect, (200, 200, 220))

    # knob
    knob_x = int(bar_x + master_volume * SLIDER_W)
    knob_r = 10
    # hover effect (semplice): ingrandisci se trascini
    r = knob_r + (3 if dragging_slider else 0)
    screen.draw.filled_circle((knob_x, bar_y), r, "white")
    screen.draw.circle((knob_x, bar_y), r, "black")

    # etichette
    screen.draw.text("Volume", midbottom=(WIDTH // 2, bar_y - 12), fontsize=28, color="white", owidth=0.5, ocolor="black")
    screen.draw.text(f"{int(master_volume * 100)}%", midtop=(WIDTH // 2, bar_y + 12), fontsize=24, color="gray")


def draw_menu():
    screen.clear()
    screen.fill((20, 20, 28))
    # Titolo
    screen.draw.text(
        "Tiny Grid Roguelike",
        center=(WIDTH // 2, MENU_TITLE_Y),
        fontsize=56, color="white", owidth=1.2, ocolor="black"
    )
    # Info stato audio
    info = f"Music: {'ON' if music_enabled else 'OFF'}   SFX: {'ON' if sfx_enabled else 'OFF'}"
    screen.draw.text(info, center=(WIDTH // 2, MENU_INFO_Y), fontsize=28, color="gray")

    # Slider volume
    draw_menu_slider()

    # Pulsanti
    for b in buttons:
        r = b["rect"]
        screen.draw.filled_rect(r, (60, 62, 85))
        screen.draw.rect(r, (200, 200, 220))
        screen.draw.text(b["label"], center=r.center, fontsize=36, color="white", owidth=0.5, ocolor="black")

    # Hint
    screen.draw.text("Click sui pulsanti • Trascina il knob per il volume • INVIO avvia • ESC esce",
                     midbottom=(WIDTH // 2, HEIGHT - 12), fontsize=22, color="gray")


def draw_ui():
    # cuori semplici
    margin = 8
    for i in range(player.hp):
        r = Rect(margin + i * (18 + 6), margin, 18, 18)
        screen.draw.filled_rect(r, (200, 60, 60))
        screen.draw.rect(r, "white")
    screen.draw.text("ESC: Menu", topright=(WIDTH - 10, 6), fontsize=24, color="gray")


def draw():
    screen.clear()
    if state == STATE_MENU:
        draw_menu()
        return

    draw_grid()
    for e in enemies:
        e.draw()
    if player:
        player.draw()
        draw_ui()

    if player and player.hp <= 0:
        screen.draw.text("GAME OVER",
                         center=(WIDTH // 2, HEIGHT // 2),
                         fontsize=72, color="white", owidth=2, ocolor="black")
        screen.draw.text("Click per tornare al Menu",
                         center=(WIDTH // 2, HEIGHT // 2 + 60),
                         fontsize=32, color="gray")


# --- Update / input ---
def update(dt):
    if state != STATE_GAME or not player:
        return
    player.update(dt)
    for e in enemies:
        e.update(dt, player)
    # danno da contatto
    for e in enemies:
        if hypot(e.x - player.x, e.y - player.y) < 28:
            player.take_hit(1)


def on_key_down(key):
    global music_enabled, sfx_enabled
    if state == STATE_MENU:
        if key == keys.ESCAPE:
            raise SystemExit
        if key == keys.RETURN:
            play_sfx("click")
            start_game()
        return

    # in gioco
    if key == keys.ESCAPE:
        back_to_menu()
        return
    if player and player.hp > 0:
        if key in (keys.LEFT, keys.A):
            player.try_move(-1, 0)
        elif key in (keys.RIGHT, keys.D):
            player.try_move(1, 0)
        elif key in (keys.UP, keys.W):
            player.try_move(0, -1)
        elif key in (keys.DOWN, keys.S):
            player.try_move(0, 1)


def _slider_hit_test(pos):
    """Ritorna True se clic su barra o knob."""
    x, y = pos
    bar_x = WIDTH // 2 - SLIDER_W // 2
    bar_y = SLIDER_Y
    # area comoda più alta della barra per facilitare il click
    rect = Rect(bar_x, bar_y - 16, SLIDER_W, 32)
    return rect.collidepoint(pos)


def _slider_set_from_pos(pos):
    x, _ = pos
    bar_x = WIDTH // 2 - SLIDER_W // 2
    t = (x - bar_x) / SLIDER_W
    set_master_volume(t)


def on_mouse_down(pos):
    global music_enabled, sfx_enabled, dragging_slider
    if state == STATE_GAME:
        if player and player.hp <= 0:
            play_sfx("click")
            back_to_menu()
        return

    # MENU
    if _slider_hit_test(pos):
        dragging_slider = True
        _slider_set_from_pos(pos)
        # aggiorna musica immediatamente se sta suonando
        try:
            music.set_volume(master_volume)
        except Exception:
            pass
        return

    for b in buttons:
        if b["rect"].collidepoint(pos):
            label = b["label"]
            play_sfx("click")
            if label == "Avvia partita":
                start_game()
            elif label == "Attiva/Disattiva musica e suoni":
                music_enabled = not music_enabled
                sfx_enabled = not sfx_enabled
                try:
                    if state == STATE_GAME:
                        if music_enabled:
                            music.play("theme")
                            music.set_volume(master_volume)
                        else:
                            music.stop()
                except Exception:
                    pass
            elif label == "Esci":
                raise SystemExit


def on_mouse_up(pos):
    global dragging_slider
    dragging_slider = False


def on_mouse_move(pos, rel, buttons):
    # trascinamento slider
    if state == STATE_MENU and dragging_slider:
        _slider_set_from_pos(pos)
        try:
            music.set_volume(master_volume)
        except Exception:
            pass


# --- Ticker animazioni (~6-7 fps) ---
def tick_animation():
    if state == STATE_GAME:
        if player:
            player.step_animation()
        for e in enemies:
            e.step_animation()


clock.schedule_interval(tick_animation, 0.15)

# imposta volume iniziale
set_master_volume(master_volume)
