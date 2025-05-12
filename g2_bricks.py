
# this creates th bricks game using the GameFixedLevel engine.

import numpy as np
import random
import pygame

from GameFixedLevel import *

# -
# parameters for the game
# -

GAME_SIZE    = [600,800]
PADDLE_SIZE  = [150,20]
PADDLE_SPEED = 5
BALL_SIZE    = [20,20]
BALL_SPEED   = 5
MIN_SPEED    = 0.6
BRICK_ROWS   = 5
BRICK_COLS   = 20
BRICK_HEIGHT = 40
FPS          = 60

# -
# game specific functions
# -

def get_random_velocity():
    v = [0.0,0.0]
    s1   = random.randint(0,1)*2-1
    v[1] = random.uniform(MIN_SPEED,BALL_SPEED-MIN_SPEED)*s1
    s2   = random.randint(0,1)*2-1
    v[0] = pow(pow(BALL_SPEED,2)-pow(v[1],2),.5)*s2
    return v

def game_always(me):
    if len(me.items['brick']) == 0 and not me.game_over:
        me.game_over = True
        me.winner = me.player
        me.player.invincible = -1
        for g in me.items['ball']:
            g.pause = -1

def ball_down(bl, box):
    bl.parent.kill_target(bl, bl.player)
    bl.rect.x,bl.rect.y = 400, 150
    bl.pause = 90
    bl.velocity = get_random_velocity()
    if bl.player.lives == 0:
        bl.parent.game_over = True
        bl.pause = -1

def ball_bounce(bl, pl):
    GameFixedLevel.bounce(bl,pl)
    div_num   = (PADDLE_SIZE[0]-BALL_SIZE[0])/2/BALL_SPEED
    sx        = np.sign(bl.rect.centerx() - pl.rect.centerx())
    dx        = (abs(bl.rect.centerx() - pl.rect.centerx())) / div_num
    bl.velocity[0] = max(MIN_SPEED,min(BALL_SPEED,dx))*sx
    bl.velocity[1] = max(MIN_SPEED,pow(pow(BALL_SPEED,2)-pow(bl.velocity[0],2),.5))*np.sign(bl.velocity[1])

def fire(me, key):
    if me.parent.counter - me.fired >=20:
        Item(me.parent, name='l', kind='bullet', size=[5, 5], init_loc=[me.rect.r().centerx, me.rect.r().top - 10], color=(0, 255, 0),
             velocity=[0,-1], collides={'box_fit': 'kill', 'brick':GameFixedLevel.kill_both})
        p.fired = me.parent.counter

def brick_dead(me):
    me.player.score += 1
    return True

def player_reset(me):
    me.fired = -20

# -
# initialization of the game
# -

game = GameFixedLevel('Bricks', ['player', 'ball', 'brick', 'bullet', 'touch'], GAME_SIZE, always=game_always, fps=FPS,
                      box=[GAME_SIZE[0], GAME_SIZE[1] - 200])


p = Item(game, name='', kind='player', size=PADDLE_SIZE, init_loc=[(GAME_SIZE[0] - PADDLE_SIZE[0]) // 2, GAME_SIZE[1] - PADDLE_SIZE[1] - 250], color=(255, 0, 0),
         moves={pygame.K_UP: [0, -PADDLE_SPEED], pygame.K_DOWN: [0, PADDLE_SPEED], pygame.K_RIGHT: [PADDLE_SPEED, 0], pygame.K_LEFT: [-PADDLE_SPEED, 0],
            pygame.K_SPACE: fire}, collides={'box_fit': 'hold'}, reset_fcn=player_reset, lives = 3)

b = Item(game, name='b1', kind='ball', size=BALL_SIZE, init_loc=[400, 150], color=(255, 255, 255), velocity=get_random_velocity(),
         draw_fcn=pygame.draw.ellipse, collides={'top': 'bounce', 'bottom': ball_down, 'left': 'bounce', 'right': 'bounce',
                                             'player':ball_bounce, 'brick': GameFixedLevel.kill_target_and_bounce})
b.player = p
game.player = p

# initializing all the bricks here
for i in range(BRICK_COLS):
    for j in range(BRICK_ROWS):
        bw = GAME_SIZE[0] // BRICK_COLS
        bh = BRICK_HEIGHT
        brick = Item(game, kind='brick', size=[bw-1, bh-1], init_loc=[i * bw, j * bh], color=(120, 120, 120), live_lost_fcn=brick_dead)
        brick.player = p

# -
# add touchpad elements for use on mobile devices.
# -

game.create_move_touchpad(p,loc=['bottom','right'])
game.create_key_touchpad (p,loc=['bottom','left' ] ,key=pygame.K_SPACE, pad_size=[100,100])
game.create_escape_touchpad(loc=['top'   ,'right'])

# -
# run the game
# -

async def main():
    await game.run()

asyncio.run(main())