from GameFixedLevel import *
import numpy as np
import random

GAME_SIZE    = [600,800]
ACTUAL_SIZE  = [600,600]
PADDLE_SIZE  = [30,100]
PADDLE_SPEED = 4.5
BALL_SIZE    = [20,20]
BALL_SPEED   = 2.5
MIN_SPEED    = 0.6
FPS          = 200

def get_random_velocity():
    v = [0.0,0.0]
    s1   = random.randint(0,1)*2-1
    v[1] = random.uniform(MIN_SPEED,BALL_SPEED-MIN_SPEED)*s1
    s2   = random.randint(0,1)*2-1
    v[0] = pow(pow(BALL_SPEED,2)-pow(v[1],2),.5)*s2
    return v

def ball_kill(bl, box, pl):
    bl.parent.kill_target(bl, pl)
    bl.rect.x, bl.rect.y = 390, 290
    bl.velocity = get_random_velocity()
    bl.pause = 90
    if pl.lives == 0:
        bl.parent.game_over = True
        if pl == bl.player_left:
            bl.parent.winner = bl.player_right
        else:
            bl.parent.winner = bl.player_left
        bl.pause = -1

def ball_left(bl, box):
    ball_kill(bl, box, bl.player_left)

def ball_right(bl, box):
    ball_kill(bl, box, bl.player_right)

def ball_bounce(bl, pl):
    GameFixedLevel.bounce(bl,pl)
    pl.score += 1
    div_num   = (PADDLE_SIZE[1]-BALL_SIZE[1])/2/BALL_SPEED
    sy        = np.sign(bl.rect.centery() - pl.rect.centery())
    dy        = (abs(bl.rect.centery() - pl.rect.centery())) / div_num
    bl.velocity[1] = max(MIN_SPEED,min(BALL_SPEED,dy))*sy
    bl.velocity[0] = max(MIN_SPEED,pow(pow(BALL_SPEED,2)-pow(bl.velocity[1],2),.5))*np.sign(bl.velocity[0])

game = GameFixedLevel('Pong', ['player','ball'],GAME_SIZE,box=ACTUAL_SIZE,text_color=(255, 255, 255),fps=FPS)
p1 = Item(game, name='left ', kind='player', size=PADDLE_SIZE, init_loc=[20, (GAME_SIZE[0] - PADDLE_SIZE[0]) // 2], color=(255, 0, 0),
          moves={pygame.K_w: [0, -PADDLE_SPEED], pygame.K_s: [0, PADDLE_SPEED], pygame.K_d: [PADDLE_SPEED, 0], pygame.K_a: [-PADDLE_SPEED, 0]},
          collides={'box_fit': 'hold'},
          lives = 3)
p2 = Item(game, name='right', kind='player', size=PADDLE_SIZE, init_loc=[GAME_SIZE[1] - PADDLE_SIZE[1] - 20, (GAME_SIZE[0] - PADDLE_SIZE[0]) // 2], color=(0, 0, 255),
          moves={pygame.K_UP: [0, -PADDLE_SPEED], pygame.K_DOWN: [0, PADDLE_SPEED], pygame.K_RIGHT: [PADDLE_SPEED, 0], pygame.K_LEFT: [-PADDLE_SPEED, 0]},
          collides={'box_fit': 'hold'},
          lives = 3)
b = Item(game, name='b', kind='ball', size=BALL_SIZE, init_loc=[(GAME_SIZE[0] - BALL_SIZE[0]) // 2, (GAME_SIZE[1] - BALL_SIZE[1]) // 2], color=(255, 255, 255), velocity=get_random_velocity(),
         draw_fcn=pygame.draw.ellipse, collides={'top': 'bounce', 'bottom': 'bounce', 'left': ball_left, 'right': ball_right,
                                                 'player': ball_bounce})
b.player_left  = p1
b.player_right = p2

game.create_move_touchpad(p2,loc=['bottom','right'])
game.create_move_touchpad(p1,loc=['bottom','left'],keys=[pygame.K_a,pygame.K_w,pygame.K_s,pygame.K_d])
game.create_escape_touchpad(loc=['top'   ,'right'])


async def main():
    await game.run()

asyncio.run(main())