
import numpy as np
import random
import names_generator
import geonamescache


class Tile:
    terrains  = ['Forest'  , 'House'  , 'Desert'  , 'Grassland'  , 'Hill'  ]
    healing   = {'Forest':1, 'House':5, 'Desert':0, 'Grassland':2, 'Hill':1}

    geo_cache = geonamescache.GeonamesCache()
    cities    = geo_cache.get_cities()
    names     = [x['name'] for x in cities.values()]

    @staticmethod
    def create():
        tile_ter = Tile.terrains[random.randint(0, len(Tile.terrains) - 1)]
        tile_nm  = Tile.names[random.randint(0, len(Tile.names) - 1)]
        # tile_nm    = tile_nm[-1].upper() + tile_nm[-2::-1]
        t = Tile(tile_nm, tile_ter)
        return t

    def __init__(self,name,terrain):
        self.name       = name
        self.terrain    = terrain
        self.characters = []
        self.items      = []

    def description(self):
        print('a '+ self.terrain + ' called ' + self.name + '.')
        print('You see ',end='')
        if len(self.characters) == 0:
            print('no one.')
        else:
            for i in self.characters:
                if i!=self.characters[0]:
                    print(',',end='')
                print('a '+ i.stats() ,end='')
            print('')

    def search(self, me):
        print('You search and find ',end='')
        if len(self.items) == 0:
            print('nothing.')
            return 0
        else:
            i = self.items.pop(0)
            me.items.append(i)
            print(i.stats(), end='')
            # for i in self.items:
            #     if i!=self.items[0]:
            #         print(',', end='')
            #     print(i.stats(),end='')
            #     me.items.append(i)
            # self.items = []
            print('')
        print(me.stats())
        return 0

    def talk(self,me,ci=0):
        if len(self.characters) == 0:
            print('There is no one to talk to.')
        else:
            c = self.characters[ci]
            print('You talk to ' + c.name + ' and he give you ' + c.information)
        return 0

    def fight(self, me, ci=0):
        if len(self.characters) == 0:
            print('There is no one to fight with.')
        else:
            c   = self.characters[ci]
            won = me.fight(c)
            if won == 1:
                print('You fight ' + c.name + ' and win.')
                return 0
            elif won == -1:
                print('You fight ' + c.name + ' and lose.')
                return 0

    def heal(self,me):
        me.heal(Tile.healing[self.terrain])

class Dungeon(Tile):
    def __init__(self, name, terrain, size, x, y):
        super().__init__(name, terrain)
        self.size = size
        self.x    = x
        self.y    = y
        self.map  = np.ndarray(shape=(size,size),dtype=Tile)

    def curr_tile(self):
        return self.map[self.x,self.y]

class GameTextAdventure(Dungeon):
    moves = { 'north':[ 0,-1], 'up':   [ 0,-1],
              'south':[ 0, 1], 'down': [ 0, 1],
              'east' :[-1, 0], 'left': [-1, 0],
              'west': [ 1, 0], 'right':[ 1, 0]
            }

    def __init__(self, name, size, char_prob=.80,char_stats_max=None,item_prob=.80):
        super().__init__(name, '', size, size//2, size//2)
        self.player        = None
        for i in range(size):
            for j in range(size):
                t = Tile.create()
                self.map[i,j] = t
                r = random.uniform(0, 1)
                if r <= char_prob:
                    t.characters.append(Character.create(char_stats_max))

                if not isinstance(item_prob,list):
                    item_prob = [item_prob]
                for it in item_prob:
                    r = random.uniform(0, 1)
                    if r <= it:
                        t.items.append(Item.create())

    @staticmethod
    def help():
        print('-----------------------------------------------------')
        print('In this game you have the following actions:')
        print(' \'move <dir>\': to move left, right, up, and down or east, west, north, and south')
        print(' \'stats\'     : to see your stats')
        print(' \'loc\'       : to know your location')
        print(' \'fight\'     : to fight entities')
        print(' \'search\'    : to search for hidden items')
        print(' \'heal\'      : to heal up')
        print(' \'help\'      : to see the commands')
        print(' \'quit\'      : to leave the game')
        print('-----------------------------------------------------')

    def start(self,me=None):
        print('-----------------------------------------------------')
        print('Welcome to '+ self.name+' you are in for an adventure')
        GameTextAdventure.help()
        if me is None:
            name = input('What is your name? ')
            self.player = Character(name,'Person', 0, 10, 2, 1)

        print('You are in a ',end='')
        self.curr_tile().description()
        result = self.do_action()
        while result != -1:
            result = self.do_action()
        print('Thank you for playing')

    def move(self,direction):
        d = direction.strip().lower()
        dx,dy = [0,0]
        if d in GameTextAdventure.moves:
            dx,dy = GameTextAdventure.moves[d]
        else:
            print(d +' is not a known direction')
            return

        new_x,new_y = [self.x + dx, self.y + dy]
        if new_x <0 or new_x >= self.size or new_y<0 or new_y>=self.size:
            print('There is a wall in that direction. You stay in you current location')
        else:
            self.x = new_x
            self.y = new_y
            print('----------------------------')
            print('You move to ('+str(self.x)+','+str(self.y)+') and have reached ...')
            self.curr_tile().description()

    def do_action(self):

        action = input('What do you want to do next? ')

        a = action.lower()
        if a == 'quit' or a == 'exit' or a == 'leave':
            return -1
        if a == 'search':
            return self.curr_tile().search(self.player)
        elif a == 'talk':
            return self.curr_tile().talk(self.player)
        elif a == 'fight':
            return self.curr_tile().fight(self.player)
        elif a == 'stats':
            print(self.player.stats())
        elif a == 'heal':
            self.curr_tile().heal(self.player)
            print(self.player.stats())
        elif a == 'help':
            GameTextAdventure.help()
        elif a == 'loc' or a == 'location':
            print('You are at ('+str(self.x)+','+str(self.y)+').')
        elif len(a)>=4 and a[:4] == 'move':
            self.move(a[5:])
        else:
            print(a+'is not a valid action. Please chose again.')
        return 0

class Character:
    kinds = ['wolf', 'person', 'robber']
    @staticmethod
    def create(max_stats=None):
        if max_stats is None:
            max_stats = [12, 5, 5]
        char_kd = Character.kinds[random.randint(0, len(Character.kinds) - 1)]
        char_nm = names_generator.generate_name(style='capital')
        health  = random.randint(1, max_stats[0])
        attack  = random.randint(1, max_stats[1])
        defense = random.randint(1, max_stats[2])
        c = Character(char_nm, char_kd, 0, health, attack, defense)
        return c

    def __init__(self,name, kind, exp=0, health=1, attack=0, defense=0):
        self.name   = name
        self.kind   = kind
        self.exp    = exp
        self.max_health  = health
        self.health = health
        self.attack = attack
        self.defense= defense
        self.skills = []
        self.items  = []
        self.information = 'no information'

    def fight(self,other):
        if other.get('health')<=0:
            print(other.stats()+' is already dead.')
            return 0
        print(self.stats() + ' X ' + other.stats())
        while self.get('health')>1 and other.get('health')>0:
            other_damage  = max(0, self.get('attack') - other.get('defense'))
            self_damage   = max(0, other.get('attack') - self.get('defense'))
            if self_damage == 0 and other_damage == 0:
                print('You two are equally matched and call it off')
                return 0
            other.health -= min(other.get('health'),other_damage)
            self.health  -= min(self.get('health')-1,self_damage)
            print(self.stats()+ ' X '+ other.stats())
        return np.sign(self.get('health') - other.get('health'))

    def stats(self):
        stats  = f"{self.kind} {self.name} "
        if len(self.items)>0:
            stats += "with "
            for i in self.items:
                if i!=self.items[0]:
                    stats += ','
                stats += i.kind
            stats += ' '
        stats += f"[health:{self.get('health')}({self.get('attack')}/{self.get('defense')})]"
        return stats

    def heal(self, h):
        self.health += min(self.get('max_health') - self.get('health'), h)

    def get(self,var):
        value = getattr(self,var)
        for i in self.items:
            value += getattr(i,var)
        return value

    def get_max_health(self):
        health = self.health
        for i in self.items:
            health += i.health

class Item:
    @staticmethod
    def create():
        item_kinds = ['Strength'  , 'Potion', 'Sword' , 'Shield' ]
        item_props = ['max_health', 'health', 'attack', 'defense']

        tp         = random.randint(0, 3)
        kind       = item_kinds[tp]
        prop       = item_props[tp]
        value      = random.randint(1, 4)
        item       = Item(kind=kind)
        item.set(prop,value)
        return item

    def __init__(self, name='', kind='', health=0, max_health=0, attack=0, defense=0):
        self.name   = name
        self.kind   = kind
        self.health  = health
        self.max_health  = max_health
        self.attack = attack
        self.defense= defense

    def set(self,var,value):
         setattr(self,var,value)

    def stats(self):
        stats = ''
        if self.kind != '':
            stats += self.kind + ' '
        if self.name != '':
            stats += self.name + ' '
        stats += 'with '
        if self.max_health != 0:
            stats += 'max health:'+str(self.max_health)
        if self.health != 0:
            stats += 'health:'+str(self.health)
        if self.attack != 0:
            stats += 'attack:'+str(self.attack)
        if self.defense != 0:
            stats += 'defense:'+str(self.defense)
        return stats
