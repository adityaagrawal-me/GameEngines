from GameFixedLevel import *
import random

GAME_SIZE    = [600,800]
FPS          = 20

def invader_reset(me):
    me.dir = -1

def space_inv(me):
    if me.parent.counter % 80 == 0:
        me.dir *= -1
        me.rect.y += 30
    if me.parent.counter % 5 == 0:
        me.rect.x += 10*me.dir
        r = random.uniform(0,1)
        if r<.020:
            Item(me.parent, name='l', kind='ibullet', size=[4, 8], init_loc=[me.rect.centerx(), me.rect.top() - 10],
                 color=(255, 0, 0),
                 velocity=[0, 3],
                 collides={'box_fit': 'kill', 'player': GameFixedLevel.kill_both, 'bullet': GameFixedLevel.kill_both})

def game_always(me):
    if len(me.items['invader']) == 0 and not me.game_over:
        me.game_over = True
        me.winner = me.player
        me.player.invincible = -1
        for g in me.items['ibullet']:
            g.pause = -1
        for g in me.items['bullet']:
            g.pause = -1

def bullet_invader(me, inv):
    GameFixedLevel.kill_both(me, inv)
    me.parent.player.score +=1


def player_reset(me):
    me.fired = -5

def fire(me,key):
    if me.parent.counter - me.fired >=5:
        Item(me.parent, name='l', kind='bullet', size=[4, 8], init_loc=[me.rect.centerx(), me.rect.top() - 10], color=(0, 255, 0),
             velocity=[0,-3], collides={'box_fit': 'kill', 'invader':bullet_invader})
        me.fired = me.parent.counter

game = GameFixedLevel('Invaders', ['player', 'invader', 'bullet', 'ibullet'], GAME_SIZE, box=[GAME_SIZE[0],GAME_SIZE[1]-200], fps=FPS, always=game_always)
p = Item(game, name='', kind='player', size=[30, 20], init_loc=[380, 550], color=(50, 180, 50),
         moves={pygame.K_UP: [0, -5], pygame.K_DOWN: [0, 5], pygame.K_RIGHT: [5, 0], pygame.K_LEFT: [-5, 0],
                pygame.K_SPACE: fire}, collides={'box_fit': 'hold'}, reset_fcn=player_reset,
         lives=3, live_lost_invincibility=30, image_bmp='invader_player.bmp', image_inv_bmp='invader_player_inv.bmp')
game.player = p

for i in range(8):
    for j in range(6):
        inv = Item(game, kind='invader', size=[36, 28], init_loc=[i * 50 + 30, j * 35], color=(200, 100, 100),
                   velocity=[0, 0], always=space_inv, reset_fcn=invader_reset,
                   collides={'box_fit': 'kill', 'player': GameFixedLevel.kill_target},
                   image_bmp='invader.bmp')

game.create_move_touchpad(p,loc=['bottom','right'])
game.create_key_touchpad (p,loc=['bottom','left' ] ,key=pygame.K_SPACE, pad_size=[100,100])
game.create_escape_touchpad(loc=['top'   ,'right'])

async def main():
    await game.run()

asyncio.run(main())