import pygame.draw

from GameFixedLevel import *
import random

GAME_SIZE    = [600,800]
ACTUAL_SIZE  = [600,600]
SNAKE_SIZE   = [20,20]
FOOD_SIZE    = [5,5]
FPS          = 60
SPEED        = 4
BUFFER       = -4

def draw_diamond(screen, color, rect):
    pygame.draw.polygon(screen, color, [[rect.centerx,rect.top],[rect.right,rect.centery],[rect.centerx,rect.bottom],[rect.left,rect.centery]])

def draw_rounded_rect(screen, color, rect):
    pygame.draw.rect(screen, color, rect,border_radius=6)


SNAKE_SHAPES  = [pygame.draw.rect,pygame.draw.ellipse,draw_diamond,draw_rounded_rect]


def snake_draw(me):
    # screen border
    pygame.draw.rect(me.screen, (120, 120, 120), pygame.Rect(0, 0, ACTUAL_SIZE[0], ACTUAL_SIZE[1]),width=SPEED)

def create_food(me):
    x = random.randint(20, ACTUAL_SIZE[0] - 25)
    y = random.randint(20, ACTUAL_SIZE[1] - 25)
    color = (random.randint(120, 255), random.randint(120, 255), random.randint(120, 255))
    food = Item(me, kind='food', size=FOOD_SIZE,
                init_loc=[x, y], color=color)


def snake_allways(me):
    if me.counter == 0 and not me.game_over:
        for i in range(20):
            create_food(me)
    if me.counter % 60 == 0 and not me.game_over:
        create_food(me)
    if me.counter % 480 == 0 and not me.game_over:
        w = random.randint(1, 5)*SNAKE_SIZE[0]
        h = random.randint(1, 5)*SNAKE_SIZE[1]
        x = random.randint(20, ACTUAL_SIZE[0] - w-20)
        y = random.randint(20, ACTUAL_SIZE[1] - h-20)
        r = pygame.Rect(x,y,w,h)
        if r.colliderect(me.player.forward_rect(60)):
            return
        color = (random.randint(20, 100), random.randint(20, 100), random.randint(20, 100))
        wall = Item(me, kind='wall', size=[w, h], init_loc=[x, y], color=color,draw_fcn=draw_rounded_rect)

def snake_key(me,key):
    if me.new_vel_cnt <=0 and key == pygame.K_SPACE:
        me.parent.pause = not me.parent.pause
        me.new_vel_cnt = 120
        return

    new_vel = None
    if me.new_vel_cnt <=0:
        if key == pygame.K_UP and me.velocity[1] == 0:
            new_vel = [ 0, -SPEED]
        elif key == pygame.K_DOWN and me.velocity[1] == 0:
            new_vel = [ 0,  SPEED]
        elif key == pygame.K_LEFT and me.velocity[0] == 0:
            new_vel = [-SPEED,  0]
        elif key == pygame.K_RIGHT and me.velocity[0] == 0:
            new_vel = [ SPEED,  0]

    if new_vel is not None:
        r = GameRect(me.rect.x+new_vel[0],me.rect.y+new_vel[1],me.rect.width,me.rect.height)
        me.velocity    = new_vel
        me.new_vel_cnt = (SNAKE_SIZE[0]+BUFFER) / SPEED + 1

def body_always(me):
    if me.new_vel_cnt == 0:
        me.velocity = me.new_vel
        me.new_vel_cnt = -1
    elif me.new_vel_cnt == -1 and (me.prev.velocity[0] != me.velocity[0] or me.prev.velocity[1] != me.velocity[1]):
        me.new_vel     = me.prev.velocity
        me.new_vel_cnt = (SNAKE_SIZE[0]+BUFFER) / SPEED
    if me.new_vel_cnt > 0:
        me.new_vel_cnt -= 1

def eat(me, other):
    GameFixedLevel.kill_target(me,other)
    new_loc = me.tail.rect.after(me.tail.velocity,BUFFER)
    me.body_cnt +=1
    me.score += 1
    color = me.color if me.body_cnt%2==0 else me.color2
    b = Item(game, name=str(me.body_cnt), kind='body', size=[20, 20], init_loc=new_loc, color=color,
             velocity=me.tail.velocity, always=body_always,draw_fcn=me.draw_fcn)
    b.prev    = me.tail
    b.new_vel_cnt = -1
    if me.tail == me:
        b.pause = 1
    me.tail = b

def player_reset(me):
    me.tail        = me
    me.body_cnt    = 0
    me.new_vel_cnt = 0
    me.velocity    = [0,0]
    me.color  = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
    me.color2 = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
    me.draw_fcn = SNAKE_SHAPES[random.randint(0,len(SNAKE_SHAPES)-1)]
    me.speed = SPEED
    me.just_died = False

def player_always(me):
    if me.new_vel_cnt > 0:
        me.new_vel_cnt -= 1
    if me.just_died and me.pause == 0:
        me.just_died = False
        me.rect = GameRect(me.init_loc[0], me.init_loc[1], me.size[0], me.size[1])
        if me.tail != me:
            tail = me.tail
            prev = tail.prev
            while prev != me:
                tail.live_lost()
                tail = prev
                prev = tail.prev
            tail.live_lost()
        player_reset(me)

def life_lost(me):
    me.just_died = True
    if me.tail != me:
        tail = me.tail
        prev = tail.prev
        while prev != me:
            tail.pause = -1
            tail = prev
            prev = tail.prev
        tail.pause = -1
    return True

def kill_if_head(me, body):
    v     = me.velocity
    front = [(0,0),(0,0)]
    if v[0] != 0: # x movement
        if v[0] > 0:
            front = [(me.rect.right(),me.rect.top()), (me.rect.right(),me.rect.bottom())]
        else:
            front = [(me.rect.left(),me.rect.top()), (me.rect.left(),me.rect.bottom())]
    elif v[1] != 0: # y movement
        if v[1] > 0:
            front = [(me.rect.left(),me.rect.bottom()), (me.rect.right(),me.rect.bottom())]
        else:
            front = [(me.rect.left(),me.rect.top()), (me.rect.right(),me.rect.top())]

    if body.rect.r().collidepoint(front[0]) or body.rect.r().collidepoint(front[1]):
        me.live_lost()


game = GameFixedLevel('Snake', ['player', 'body', 'food', 'wall'], GAME_SIZE, box=ACTUAL_SIZE, fps=FPS,
                      always=snake_allways, draw=snake_draw)

p = Item(game, name='', kind='player', size=[20, 20], init_loc=[ACTUAL_SIZE[0] / 2, ACTUAL_SIZE[1] / 2],
         moves={pygame.K_UP: snake_key, pygame.K_DOWN: snake_key, pygame.K_RIGHT: snake_key, pygame.K_LEFT: snake_key, pygame.K_SPACE:snake_key},
         always=player_always, collides={'box_fit': 'kill', 'food': eat, 'wall': 'kill me', 'body': kill_if_head},
         lives=3, live_lost_pause=60, live_lost_invincibility=60, reset_fcn=player_reset, live_lost_fcn=life_lost)
game.player = p

game.create_move_touchpad(p,loc=['bottom','right'])
game.create_escape_touchpad(loc=['top','right'])

async def main():
    await game.run()

#asyncio.run(main())