from pygame import Rect
from math import hypot
from random import choice, randint

TILE=64
COLS,ROWS=10,8
WIDTH,HEIGHT=COLS * TILE, ROWS * TILE

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

def is_blocked(gx,gy):
    if gx <0 or gy <0 or gx >= COLS or gy >= ROWS:
        return True
    return LEVEL[gy][gx] =="#"

def grid_to_px(gx,gy):
    return gx * TILE + TILE // 2, gy * TILE + TILE // 2

class Player:

    def __init__(self,gx,gy,idle_frames=None,speed=260.0):
        self.gx = gx
        self.gy = gy
        self.x,self.y= grid_to_px(gx,gy)
        self.tx,self.ty= self.x,self.y
        self.moving= False
        self.speed = speed


        self.idle_frames=idle_frames or [
            "hero_idle_0","hero_idle_1","hero_idle_2","hero_idle_3"
        ]
        self.frame_index=0

        try:
            self.actor= Actor(self.idle_frames[0], anchor=("center","center"))
            self.actor.pos=(self.x,self.y)
        except Exception:
            self.actor=None

        clock.schedule_interval(self.step_idle_animation,0.16)

    def try_move(self,dx,dy):
        if self.moving:
            return
        ngx,ngy= self.gx + dx, self.gy + dy
        if is_blocked(ngx,ngy):
            return
        self.gx,self.gy= ngx,ngy
        self.tx,self.ty= grid_to_px(self.gx,self.gy)
        self.moving= True

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

    def step_idle_animation(self):
        if not self.actor:
            return
        self.frame_index = (self.frame_index + 1) % len(self.idle_frames)
        self.actor.image = self.idle_frames[self.frame_index]

    def draw(self):
        if self.actor:
            self.actor.pos = (self.x, self.y)
            self.actor.draw()
        else:
            # segnaposto se mancano immagini
            screen.draw.filled_circle((self.x, self.y), 20, "white")
            screen.draw.circle((self.x, self.y), 20, "black")


player = Player(1, 1)

def draw_grid():
    for y in range(ROWS):
        for x in range(COLS):
            rect = Rect(x * TILE, y * TILE, TILE, TILE)
            if LEVEL[y][x] == "#":
                screen.draw.filled_rect(rect, "dimgray")
            else:
                screen.draw.filled_rect(rect, "lightgray")
            screen.draw.rect(rect, "black")

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
        exit()
    elif key in (keys.UP, keys.W):
        player.try_move(0, -1)
    elif key in (keys.DOWN, keys.S):
        player.try_move(0, 1)
    elif key in (keys.LEFT, keys.A):
        player.try_move(-1, 0)
    elif key in (keys.RIGHT, keys.D):
        player.try_move(1, 0)