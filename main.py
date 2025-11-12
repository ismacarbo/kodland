

from pygame import Rect
from random import choice, randint

TITLE = "RogueLite - Step 3 (Enemies move)"
TILE = 64
COLS, ROWS = 10, 8
WIDTH, HEIGHT = COLS * TILE, ROWS * TILE


STATE_MENU = "menu"
STATE_GAME = "game"
state = STATE_MENU


music_enabled = True
sfx_enabled = True


LEVEL = [
    "
    "
    "
    "
    "
    "
    "
    "
]


def grid_to_px(gx, gy):
    return gx * TILE + TILE // 2, gy * TILE + TILE // 2


def is_blocked(gx, gy):
    if gx < 0 or gy < 0 or gx >= COLS or gy >= ROWS:
        return True
    return LEVEL[gy][gx] == "


class GridMover:
    """Base: coord a griglia, destinazione a pixel, interpolazione fluida."""
    def __init__(self, gx, gy, speed=240.0):
        self.gx, self.gy = gx, gy
        self.x, self.y = grid_to_px(gx, gy)
        self.tx, self.ty = self.x, self.y
        self.moving = False
        self.speed = speed

    def start_move(self, dx, dy):
        if self.moving:
            return False
        nx, ny = self.gx + dx, self.gy + dy
        if is_blocked(nx, ny):
            return False
        self.gx, self.gy = nx, ny
        self.tx, self.ty = grid_to_px(nx, ny)
        self.moving = True
        return True

    def update_motion(self, dt):
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


class Player(GridMover):
    """Player con animazione idle."""
    def __init__(self, gx, gy, idle_frames=None, speed=260.0):
        super().__init__(gx, gy, speed=speed)
        self.idle_frames = idle_frames or [
            "hero_idle_0", "hero_idle_1", "hero_idle_2", "hero_idle_3"
        ]
        self.frame_index = 0
        try:
            self.actor = Actor(self.idle_frames[0], anchor=("center", "center"))
            self.actor.pos = (self.x, self.y)
        except Exception:
            self.actor = None

    def try_move(self, dx, dy):
        self.start_move(dx, dy)

    def step_idle_animation(self):
        if not self.actor:
            return
        self.frame_index = (self.frame_index + 1) % len(self.idle_frames)
        self.actor.image = self.idle_frames[self.frame_index]

    def update(self, dt):
        self.update_motion(dt)

    def draw(self):
        if self.actor:
            self.actor.pos = (self.x, self.y)
            self.actor.draw()
        else:
            screen.draw.filled_circle((self.x, self.y), 20, "white")
            screen.draw.circle((self.x, self.y), 20, "black")


class Enemy(GridMover):
    """Nemico che vaga e talvolta insegue il player. Idle anim (e walk se presente)."""
    def __init__(self, gx, gy, idle_frames=None, walk_frames=None, speed=180.0):
        super().__init__(gx, gy, speed=speed)
        
        self.idle_frames = idle_frames or ["slime_idle_0", "slime_idle_1", "slime_idle_2"]
        self.walk_frames = walk_frames or self.idle_frames
        self.state = "idle"  
        self.frame_index = 0
        try:
            self.actor = Actor(self.idle_frames[0], anchor=("center", "center"))
            self.actor.pos = (self.x, self.y)
        except Exception:
            self.actor = None

        self.decide_timer = 0.0

    def decide_direction(self, player):
        """55%: muovi verso player su un asse; 45%: vagabonda."""
        if randint(0, 100) < 55:
            dx = 1 if player.gx > self.gx else -1 if player.gx < self.gx else 0
            dy = 1 if player.gy > self.gy else -1 if player.gy < self.gy else 0
            
            if dx != 0 and dy != 0:
                if randint(0, 1) == 0:
                    dy = 0
                else:
                    dx = 0
            return dx, dy
        return choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

    def step_animation(self):
        if not self.actor:
            return
        frames = self.walk_frames if self.moving else self.idle_frames
        self.frame_index = (self.frame_index + 1) % len(frames)
        self.actor.image = frames[self.frame_index]

    def update(self, dt, player):
        
        self.decide_timer -= dt
        if not self.moving and self.decide_timer <= 0:
            self.decide_timer = 0.35 + randint(0, 20) * 0.01
            dx, dy = self.decide_direction(player)
            moved = self.start_move(dx, dy)
            self.state = "walk" if moved else "idle"
        
        was_moving = self.moving
        self.update_motion(dt)
        self.state = "walk" if self.moving else "idle"
        

    def draw(self):
        if self.actor:
            self.actor.pos = (self.x, self.y)
            self.actor.draw()
        else:
            
            screen.draw.filled_circle((self.x, self.y), 18, (120, 200, 120))
            screen.draw.circle((self.x, self.y), 18, "black")



player = None
enemies = []


BUTTON_W, BUTTON_H, BUTTON_GAP = 300, 64, 16
buttons = []


def build_buttons():
    center_x = WIDTH // 2
    base_y = HEIGHT // 2 - (BUTTON_H * 1.5 + BUTTON_GAP * 1.0)
    labels = ["Start Game", "Toggle Music + SFX", "Exit"]
    out = []
    for i, label in enumerate(labels):
        r = Rect(0, 0, BUTTON_W, BUTTON_H)
        r.center = (center_x, base_y + i * (BUTTON_H + BUTTON_GAP))
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


def back_to_menu():
    global state
    state = STATE_MENU



def draw_grid():
    for gy in range(ROWS):
        for gx in range(COLS):
            x, y = gx * TILE, gy * TILE
            r = Rect(x, y, TILE, TILE)
            if LEVEL[gy][gx] == "
                screen.draw.filled_rect(r, (35, 40, 60))
            else:
                screen.draw.filled_rect(r, (24, 26, 36))
            screen.draw.rect(r, (15, 15, 22))


def draw_menu():
    screen.clear()
    screen.fill((20, 20, 28))
    screen.draw.text(
        "Tiny Grid Roguelike — Menu",
        center=(WIDTH // 2, HEIGHT // 4),
        fontsize=48, color="white", owidth=1.0, ocolor="black"
    )
    info = f"Music: {'ON' if music_enabled else 'OFF'}   SFX: {'ON' if sfx_enabled else 'OFF'}"
    screen.draw.text(info, center=(WIDTH // 2, HEIGHT // 4 + 40), fontsize=28, color="gray")

    for b in buttons:
        r = b["rect"]
        screen.draw.filled_rect(r, (60, 62, 85))
        screen.draw.rect(r, (200, 200, 220))
        screen.draw.text(b["label"], center=r.center, fontsize=36, color="white", owidth=0.5, ocolor="black")

    screen.draw.text("Click sui pulsanti • ESC per uscire",
                     midbottom=(WIDTH // 2, HEIGHT - 10),
                     fontsize=24, color="gray")


def draw_ui():
    screen.draw.text("Step 3 — ESC: torna al Menu", topright=(WIDTH - 10, 6), fontsize=24, color="gray")
    screen.draw.text(f"Enemies: {len(enemies)}", topleft=(10, 6), fontsize=24, color="gray")


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



def update(dt):
    if state != STATE_GAME or not player:
        return
    player.update(dt)
    for e in enemies:
        e.update(dt, player)


def on_key_down(key):
    if state == STATE_MENU:
        if key == keys.ESCAPE:
            raise SystemExit
        if key == keys.RETURN:
            start_game()
        return

    
    if key == keys.ESCAPE:
        back_to_menu()
        return
    if key in (keys.LEFT, keys.A):
        player.try_move(-1, 0)
    elif key in (keys.RIGHT, keys.D):
        player.try_move(1, 0)
    elif key in (keys.UP, keys.W):
        player.try_move(0, -1)
    elif key in (keys.DOWN, keys.S):
        player.try_move(0, 1)


def on_mouse_down(pos):
    global music_enabled, sfx_enabled
    if state != STATE_MENU:
        return
    for b in buttons:
        if b["rect"].collidepoint(pos):
            label = b["label"]
            if label == "Start Game":
                start_game()
            elif label == "Toggle Music + SFX":
                music_enabled = not music_enabled
                sfx_enabled = not sfx_enabled
            elif label == "Exit":
                raise SystemExit



def tick_animation():
    if state != STATE_GAME:
        return
    if player:
        player.step_idle_animation()
    for e in enemies:
        e.step_animation()


clock.schedule_interval(tick_animation, 0.16)  
