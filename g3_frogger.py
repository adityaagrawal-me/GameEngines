from GameFixedLevel import *
import random

GAME_SIZE    = [600,800]
ACTUAL_SIZE  = [600,600]
LANES        = 5
FPS          = 60
LANE_WIDTH   = GAME_SIZE[0]//(LANES+2) # for the left ad right side

def frogger_draw(me):
    #border
    pygame.draw.rect(me.screen, (120, 120, 120), pygame.Rect(                      0, 0, LANE_WIDTH, ACTUAL_SIZE[1]))
    pygame.draw.rect(me.screen, (120, 120, 120), pygame.Rect(GAME_SIZE[0]-LANE_WIDTH, 0, LANE_WIDTH, ACTUAL_SIZE[1]))
    for i in range(LANE_WIDTH,GAME_SIZE[0]-LANE_WIDTH,LANE_WIDTH):
        pygame.draw.rect(me.screen, (255, 255, 255), pygame.Rect(i,0,5,ACTUAL_SIZE[1]))

def frogger_always(me):
    row_prob    = [.1,.1, .15,.2, .2]
    row_dir     = [-1, 1, -1,  1, -1]
    row_speed   = [ 1, 2,  3,  5, 16]
    xsize_range = [int(LANE_WIDTH*.4),  int(LANE_WIDTH*.8)]
    ysize_range = [50,90]

    if me.counter % 10 == 0 and not me.game_over:
        for it in range(len(row_prob)):
            r = random.uniform(0, 1)
            if r <= row_prob[it]:
                y = 5
                if row_dir[it] == -1:
                    y = 550
                size  = [random.randint(*xsize_range),random.randint(*ysize_range)]
                color = (random.randint(150,255),random.randint(150,255),random.randint(150,255))
                car = Item(me, kind='car', size=size, init_loc=[LANE_WIDTH + (it * LANE_WIDTH) + (LANE_WIDTH - size[0]) // 2 , y], color=color,
                           velocity=[0, row_speed[it]*row_dir[it]], collides={'box_fit': 'kill', 'player': GameFixedLevel.kill_target})
    if me.player.score >=2:
        me.game_over = True
        me.player.invincible = -1
        me.winner = me.player
        for c in me.items['car']:
            c.pause = -1

def player_reset(me):
    me.target = 'right'

def player_always(me):
    if me.target == 'right' and me.rect.x>= GAME_SIZE[0]-LANE_WIDTH:
        me.score += 1
        me.target = 'left'
    if me.target == 'left' and me.rect.x<= LANE_WIDTH:
        me.score += 1
        me.target = 'right'

game = GameFixedLevel('Frogger',['player','car'],GAME_SIZE,box=ACTUAL_SIZE,fps=FPS,always=frogger_always,draw=frogger_draw)

p = Item(game, name='', kind='player', size=[30, 20], init_loc=[50, 300], color=(50, 180, 50),
         moves={pygame.K_UP: [0, -3.5], pygame.K_DOWN: [0, 3.5], pygame.K_RIGHT: [3.5, 0], pygame.K_LEFT: [-3.5, 0]},
         always=player_always, collides={'box_fit': 'hold'}, lives=3, live_lost_invincibility=60, reset_fcn=player_reset)
game.player = p

game.create_move_touchpad(p,loc=['bottom','right'])
game.create_escape_touchpad(loc=['top','right'])

async def main():
    await game.run()

asyncio.run(main())