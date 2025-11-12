# main_step1.py — Player in classe + animazione idle
# Dipendenze: PgZero (+ Rect da pygame, consentito)
from pygame import Rect

TITLE = "RogueLite - Step 1 (Player class + idle anim)"
TILE = 64
COLS, ROWS = 10, 8
WIDTH, HEIGHT = COLS * TILE, ROWS * TILE

# Mappa semplice (# = muro, . = pavimento). Bordi per confinare il player.
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


class Player:
    """Player con coordinate a griglia, movimento fluido e animazione idle."""

    def __init__(self, gx, gy, idle_frames=None, speed=260.0):
        self.gx, self.gy = gx, gy               # celle
        self.x, self.y = grid_to_px(gx, gy)     # pixel
        self.tx, self.ty = self.x, self.y       # target pixel (prossima cella)
        self.moving = False
        self.speed = speed

        # Frames di animazione idle
        self.idle_frames = idle_frames or [
            "hero_idle_0", "hero_idle_1", "hero_idle_2", "hero_idle_3"
        ]
        self.frame_index = 0

        # Prova a creare l'Actor. Se non ci sono asset, usiamo segnaposto.
        try:
            self.actor = Actor(self.idle_frames[0], anchor=("center", "center"))
            self.actor.pos = (self.x, self.y)
        except Exception:
            self.actor = None

        # Ticker animazione idle (6 fps circa)
        clock.schedule_interval(self.step_idle_animation, 0.16)

    # ---- input / movimento a celle ----
    def try_move(self, dx, dy):
        if self.moving:
            return
        nx, ny = self.gx + dx, self.gy + dy
        if is_blocked(nx, ny):
            return
        self.gx, self.gy = nx, ny
        self.tx, self.ty = grid_to_px(nx, ny)
        self.moving = True

    # ---- update interpolazione ----
    def update(self, dt):
        if not self.moving:
            return
        vx, vy = self.tx - self.x, self.ty - self.y
        dist2 = vx * vx + vy * vy
        if dist2 == 0:
            self.moving = False
            return
        step = self.speed * dt
        dist = dist2 ** 0.5
        if dist <= step:
            self.x, self.y = self.tx, self.ty
            self.moving = False
        else:
            self.x += (vx / dist) * step
            self.y += (vy / dist) * step

    # ---- animazione idle ----
    def step_idle_animation(self):
        if not self.actor:
            return
        self.frame_index = (self.frame_index + 1) % len(self.idle_frames)
        self.actor.image = self.idle_frames[self.frame_index]

    # ---- draw ----
    def draw(self):
        if self.actor:
            self.actor.pos = (self.x, self.y)
            self.actor.draw()
        else:
            # segnaposto se mancano immagini
            screen.draw.filled_circle((self.x, self.y), 20, "white")
            screen.draw.circle((self.x, self.y), 20, "black")


# --- istanze di gioco ---
player = Player(1, 1)


def draw_grid():
    """Sfondo minimale senza tiles grafiche: rettangoli colorati."""
    for gy in range(ROWS):
        for gx in range(COLS):
            x, y = gx * TILE, gy * TILE
            r = Rect(x, y, TILE, TILE)
            if LEVEL[gy][gx] == "#":
                screen.draw.filled_rect(r, (35, 40, 60))
            else:
                screen.draw.filled_rect(r, (24, 26, 36))
            screen.draw.rect(r, (15, 15, 22))


def draw_ui():
    screen.draw.text(
        "Step 1 — Arrow/WASD per muovere • ESC per uscire",
        topright=(WIDTH - 8, 8), fontsize=24, color="gray"
    )
    screen.draw.text(
        "Idle anim attiva (cambia frame ogni ~0.16s)",
        midbottom=(WIDTH // 2, HEIGHT - 8), fontsize=24, color="gray"
    )


def draw():
    screen.clear()
    draw_grid()
    player.draw()
    draw_ui()


def update(dt):
    player.update(dt)


def on_key_down(key):
    if key == keys.ESCAPE:
        raise SystemExit
    if key in (keys.LEFT, keys.A):
        player.try_move(-1, 0)
    elif key in (keys.RIGHT, keys.D):
        player.try_move(1, 0)
    elif key in (keys.UP, keys.W):
        player.try_move(0, -1)
    elif key in (keys.DOWN, keys.S):
        player.try_move(0, 1)
