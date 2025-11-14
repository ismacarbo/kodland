











from pygame import Rect  
from math import hypot
from random import choice, randint


TITLE = "Tiny Grid Roguelike — Final"
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


def play_sfx(name):
    if not sfx_enabled:
        return
    try:
        getattr(sounds, name).play()
    except Exception:
        pass


class AnimatedActor:
    """Attore su griglia con animazione idle/walk e interpolazione tra celle."""

    def __init__(self, idle_frames, walk_frames, gx, gy, speed=220):
        
        self.idle_frames = idle_frames or ["hero_idle_0"]
        self.walk_frames = walk_frames or self.idle_frames

        
        try:
            self.actor = Actor(self.idle_frames[0], anchor=("center", "center"))
        except Exception:
            self.actor = None

        
        self.gx, self.gy = gx, gy
        self.x, self.y = grid_to_px(gx, gy)
        self.tx, self.ty = self.x, self.y
        if self.actor:
            self.actor.pos = (self.x, self.y)

        
        self.speed = speed
        self.moving = False
        self.state = "idle"  
        self.frame_index = 0

    
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
    
    try:
        music.set_volume(0.8)
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
        "Tiny Grid Roguelike",
        center=(WIDTH // 2, HEIGHT // 4),
        fontsize=56,
        color="white",
        owidth=1.2,
        ocolor="black",
    )
    info = f"Music: {'ON' if music_enabled else 'OFF'}   SFX: {'ON' if sfx_enabled else 'OFF'}"
    screen.draw.text(info, center=(WIDTH // 2, HEIGHT // 4 + 44), fontsize=28, color="gray")

    for b in buttons:
        r = b["rect"]
        screen.draw.filled_rect(r, (60, 62, 85))
        screen.draw.rect(r, (200, 200, 220))
        screen.draw.text(b["label"], center=r.center, fontsize=36, color="white", owidth=0.5, ocolor="black")

    screen.draw.text("Click sui pulsanti • INVIO avvia • ESC esce",
                     midbottom=(WIDTH // 2, HEIGHT - 12), fontsize=24, color="gray")


def draw_ui():
    
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
        screen.draw.text(
            "GAME OVER",
            center=(WIDTH // 2, HEIGHT // 2),
            fontsize=72,
            color="white",
            owidth=2,
            ocolor="black",
        )
        screen.draw.text(
            "Click per tornare al Menu",
            center=(WIDTH // 2, HEIGHT // 2 + 60),
            fontsize=32,
            color="gray",
        )



def update(dt):
    if state != STATE_GAME or not player:
        return

    player.update(dt)
    for e in enemies:
        e.update(dt, player)

    
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


def on_mouse_down(pos):
    global music_enabled, sfx_enabled
    if state == STATE_GAME:
        if player and player.hp <= 0:
            play_sfx("click")
            back_to_menu()
        return

    
    for b in buttons:
        if b["rect"].collidepoint(pos):
            label = b["label"]
            play_sfx("click")
            if label == "Start Game":
                start_game()
            elif label == "Toggle Music + SFX":
                music_enabled = not music_enabled
                sfx_enabled = not sfx_enabled
                try:
                    if music_enabled and state == STATE_GAME:
                        music.play("theme")
                    else:
                        music.stop()
                except Exception:
                    pass
            elif label == "Exit":
                raise SystemExit



def tick_animation():
    if state == STATE_GAME:
        if player:
            player.step_animation()
        for e in enemies:
            e.step_animation()


clock.schedule_interval(tick_animation, 0.15)
