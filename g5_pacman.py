from GameFixedLevel import *
import math
import random

GAME_SIZE    = [600,800]
ACTUAL_SIZE  = [600,600]
TILE_SIZE    = [30,30]
DOT_SIZE     = [6,6]
PAC_COLOR    = [255,200,20]
SPEED        = 3
WALL_COLOR   = [25, 100,200]
GHOST_COLOR  = [[255, 0,0],[0, 255,250],[0, 100,255],[100, 255,100]]
GHOST_SPEED  = [1.5,2.5,3.5,4]
FPS          = 60
layout = [
            '                    ', # 0
            '--------------------', # 1
            '|........||........|', # 2
            '|.---.--.||.--.---.|', # 3
            '|..................|', # 4
            '|.---.|.----.|.---.|', # 5
            '|.....|......|.....|', # 6
            '-----.|--- --|.-----', # 7
            '    |.|      |.|    ', # 8
            '-----.  || |  .-----', # 9
            '     .| || | |.     ', #10
            '-----.  ||-|  .-----', # 9
            '    |.|      |.|    ', # 8
            '-----.|-- ---|.-----', # 7
            '|.....|......|.....|', # 6
            '|.---.|.----.|.---.|', # 5
            '|..................|', # 4
            '|.---.--.||.--.---.|', # 3
            '|........||........|', # 2
            '--------------------', # 1
]


def ghost_always(me):
    i = me.check_if_collides_with(me.rect, 'wall')
    if i is not None:
        GameFixedLevel.bounce(me,i.rect)
    avels = [me.velocity]
    vels  = [[me.velocity[1], me.velocity[0]],[me.velocity[1]*-1, me.velocity[0]*-1]]
    for v in vels:
        r = GameRect(me.rect.x+v[0],me.rect.y+v[1],me.rect.width,me.rect.height)
        i = me.check_if_collides_with(r,'wall')
        if i is None:
            avels.append(v)
    if len(avels)>0:
        me.velocity = random.choice(avels)


def create_ghost(cnt):
    ghost = Item(game, name='', kind='ghost', size=TILE_SIZE, init_loc=[10 * TILE_SIZE[0], 10 * TILE_SIZE[1]],
                 color=GHOST_COLOR[cnt], adv_draw_fcn=draw_ghost,
                 draw_fcn=pygame.draw.ellipse, velocity=[0, -GHOST_SPEED[cnt]], always=ghost_always,
                 collides={'top': 'wrap', 'bottom': 'wrap', 'left': 'wrap', 'right': 'wrap',
                       'player': GameFixedLevel.kill_target})

def game_always(me):
    if me.counter == 0:
        create_ghost(0)
    if me.counter == 600:
        create_ghost(1)
    if me.counter == 900:
        create_ghost(2)
    if me.counter == 1200:
        create_ghost(3)

    if len(me.items['dot']) == 0 and not me.game_over:
        me.game_over = True
        me.winner = me.player
        me.player.invincible = -1
        for g in me.items['ghost']:
            g.pause = -1

def pacman_key(me,key):
    i = me.check_if_collides_with(me.rect, 'wall')
    if i is not None:
        GameFixedLevel.push_out(me.rect,i.rect)
    new_vel = None
    if key == pygame.K_UP:
        new_vel = [ 0, -SPEED]
    elif key == pygame.K_DOWN:
        new_vel = [ 0,  SPEED]
    elif key == pygame.K_LEFT:
        new_vel = [-SPEED,  0]
    elif key == pygame.K_RIGHT:
        new_vel = [ SPEED,  0]

    if new_vel is not None:
        r = GameRect(me.rect.x+new_vel[0],me.rect.y+new_vel[1],me.rect.width,me.rect.height)
        i = me.check_if_collides_with(r,'wall')
        if i is None:
            me.velocity = new_vel

def draw_wall(surface, color, rect):
    pygame.draw.rect(surface, color, rect,width=2, border_radius=6)

def draw_pacman(me,invincible):
    if invincible:
        color = [c//2 for c in me.color]
    else:
        color = me.color

    r = me.rect.r()
    pygame.draw.ellipse(me.parent.screen, color, r)

    if (me.parent.counter//10)%2:
        if me.velocity[0]>0:
            pygame.draw.arc(me.parent.screen, [0,0,0], r,math.radians(-30),math.radians(30),20)
        elif me.velocity[0]<0:
            pygame.draw.arc(me.parent.screen, [0, 0, 0], r, math.radians(150), math.radians(210), 20)
        elif me.velocity[1]<0:
            pygame.draw.arc(me.parent.screen, [0, 0, 0], r, math.radians(60), math.radians(120), 20)
        else:
            pygame.draw.arc(me.parent.screen, [0, 0, 0], r, math.radians(240), math.radians(300), 20)

def draw_ghost(me,invincible):
    r = me.rect.r()
    pygame.draw.ellipse(me.parent.screen, me.color, r)
    pygame.draw.rect(me.parent.screen, me.color,
                     pygame.Rect(r.x, r.y + r.height // 2, r.width, r.height // 2))
    pygame.draw.ellipse(me.parent.screen, [255, 255, 255],
                        pygame.Rect(r.x + r.width * 1 // 3 -5, r.y + r.height // 3, 10, 14))
    pygame.draw.ellipse(me.parent.screen, [255, 255, 255],
                        pygame.Rect(r.x + r.width * 2 // 3 -5, r.y + r.height // 3, 10, 14))
    pygame.draw.ellipse(me.parent.screen, [0, 0, 0],
                        pygame.Rect(r.x + r.width * 1 // 3 -4, r.y + r.height // 3+4, 8, 8))
    pygame.draw.ellipse(me.parent.screen, [0, 0, 0],
                        pygame.Rect(r.x + r.width * 2 // 3 -4, r.y + r.height // 3+4, 8, 8))


game = GameFixedLevel('Pac-Man',['player','wall','dot','ghost'],GAME_SIZE,box=ACTUAL_SIZE,fps=FPS,always=game_always)

game.player = Item(game, name='', kind='player', size=TILE_SIZE, init_loc=TILE_SIZE, color=PAC_COLOR,
                   velocity=[SPEED, 0], adv_draw_fcn=draw_pacman,
                   moves={pygame.K_UP: pacman_key, pygame.K_DOWN: pacman_key, pygame.K_RIGHT: pacman_key,
                pygame.K_LEFT: pacman_key},
                   collides={'top': 'wrap', 'bottom': 'wrap', 'left': 'wrap', 'right': 'wrap', 'wall': GameFixedLevel.hold,
                   'dot': GameFixedLevel.kill_target_and_score}, lives=3, live_lost_invincibility=60)

for i in range(len(layout[0])):
    wall_start = None
    for j in range(len(layout)):
        c = layout[j][i]
        if c =='|': #wall
            if wall_start is None:
                wall_start = j
        if c != '|':
            if wall_start is not None:  # wall
                p = Item(game, name='', kind='wall', size=[TILE_SIZE[0], TILE_SIZE[1] * (j - wall_start)],
                         init_loc=[i * TILE_SIZE[0], wall_start * TILE_SIZE[1]], color=WALL_COLOR,
                         draw_fcn=draw_wall, collides={'box_fit': 'hold', })
                wall_start = None
    if wall_start is not None:
        p = Item(game, name='', kind='wall', size=[TILE_SIZE[0], TILE_SIZE[1] * (len(layout) - wall_start)],
                 init_loc=[i * TILE_SIZE[0], wall_start * TILE_SIZE[1]],
                 color=WALL_COLOR,
                 draw_fcn=draw_wall, collides={'box_fit': 'hold', })

for i in range(len(layout)):
    l = layout[i]
    wall_start = None
    for j in range(len(l)):
        if l[j]=='-': #wall
            if wall_start is None:
                wall_start = j
        if l[j] != '-':
            if wall_start is not None:  # wall
                p = Item(game, name='', kind='wall', size=[TILE_SIZE[0] * (j - wall_start), TILE_SIZE[1]],
                         init_loc=[wall_start * TILE_SIZE[0], i * TILE_SIZE[1]], color=WALL_COLOR,
                         draw_fcn=draw_wall, collides={'box_fit': 'hold', })
                wall_start = None
    if wall_start is not None:
        p = Item(game, name='', kind='wall', size=[TILE_SIZE[0] * (len(l) - wall_start), TILE_SIZE[1]],
                 init_loc=[wall_start * TILE_SIZE[0], i * TILE_SIZE[1]],
                 color=WALL_COLOR,
                 draw_fcn=draw_wall, collides={'box_fit': 'hold', })

for i in range(len(layout)):
    l = layout[i]
    wall_start = None
    for j in range(len(l)):
        if l[j]=='.':
            Item(game, name='', kind='dot', size=DOT_SIZE, init_loc=[j * TILE_SIZE[0] + (TILE_SIZE[0] - DOT_SIZE[0]) // 2,
                                                                     i * TILE_SIZE[1] + (TILE_SIZE[1] - DOT_SIZE[1]) // 2],
                 color=PAC_COLOR
                 )

game.create_move_touchpad(game.player,loc=['bottom','right'])
game.create_escape_touchpad(loc=['top','right'])

async def main():
    await game.run()

asyncio.run(main())