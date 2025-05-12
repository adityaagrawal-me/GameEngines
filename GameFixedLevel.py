import asyncio
import copy

import pygame
import pygame.freetype

class GameRect:
    """"GameRect is used to store a rect in floats and it interacts with pygame.Rect"""
    def __init__(self,x,y,w,h):
        self.x      = float(x)
        self.y      = float(y)
        self.width  = float(w)
        self.height = float(h)

    def r(self):
        return pygame.Rect(int(self.x+.5),int(self.y+.5),int(self.width+.5),int(self.height+.5))

    def centerx(self):
        return self.x+self.width/2

    def centery(self):
        return self.y+self.height/2

    def clamp_ip(self, rect):
        r = self.r()
        r.clamp_ip(rect)
        self.x = float(r.x)
        self.y = float(r.y)

    def top(self):
        return self.y

class GameFixedLevel:
    """GameFixedLevel is the class that encompasses the game and provides the run method. There are many ways to customize the behavior of the class"""

    def __init__(self, name, item_kinds, screen_size=(800, 600), background_color=(0, 0, 0), text_color=(50, 255, 255), fps=60,
                 level=1, always=None, draw=None, moves=None, box=None):

        # Initialize Pygame
        pygame.init()

        # Constants
        self.screen_size = screen_size
        self.background_color = background_color
        self.text_color  = text_color
        self.name        = name
        self.keys        = {}
        self.items       = {}
        for i in item_kinds:
            self.items[i] = []

        self.clock       = []
        self.fps         = fps
        self.level       = level
        self.always      = always
        self.draw_fcn    = draw
        self.init_items  = None
        if moves is None:
            moves       = {}
        self.moves      = moves
        self.init_box   = box
        self.box        = None

        # Set up screen
        self.screen = pygame.display.get_surface()
        if self.screen is None:
            self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption(self.name)

        self.font      = pygame.font.SysFont('consolas', 20)
        self.font_over = pygame.font.SysFont('consolas', 30)

        self.resetting = False
        self.reset()
        self.exception_message = None
        self.do_reset = False

    def reset(self):

        if not self.resetting:
            self.resetting     = True
            self.counter       = 0
            self.game_over     = False
            self.winner        = None
            self.mouse_pressed = False
            self.mouse_pos     = None
            self.finger_pos    = {}

            if self.init_box is not None:
                self.box = pygame.Rect(0,0,*self.init_box)

            if self.init_items is not None:
                self.items = {}
                for i in self.init_items.keys():
                    self.items[i] = copy.copy(self.init_items[i])

            for i in self.items.values():
                for j in i:
                    j.reset()
            self.resetting = False

    def update(self):
        # Key actions
        if self.keys[pygame.K_ESCAPE] or self.do_reset:
            self.reset()
            self.do_reset = False

        for i in self.moves.keys():
            if self.keys[i]:
                key_action = self.moves[i]
                if callable(key_action):
                    key_action(self,i)
        if self.always is not None:
            self.always(self)

    def get_box(self):
        if self.box is not None:
            return self.box
        else:
            return self.screen.get_rect()

    def add_item(self,item):
        if item.kind in self.items:
            self.items[item.kind].append(item)
        else:
            self.items[item.kind] = [item]

    def remove_item(self,item):
        if item.kind in self.items:
            try:
                self.items[item.kind].remove(item)
            except ValueError:
                pass

    def draw_text(self):

        text_line = 0
        if self.exception_message is not None:
            text = self.font.render(self.exception_message, True, self.text_color)
            self.screen.blit(text, (2, text_line * 20 + 5))
            text_line += 1

        over = True
        if 'player' in self.items:
            players = self.items['player']
            for p in players:
                name_str = p.name
                if name_str != '':
                    name_str += ' '
                text = self.font.render(f"{name_str}lives={p.lives} score={p.score}", True, self.text_color)
                self.screen.blit(text,(2,text_line*20+2))
                text_line +=1
                if p.lives>0:
                    over = False

        self.game_over = self.game_over or over
        if self.game_over:
            text_str = "GAME OVER."
            if self.winner is None:
                text_str += f' You Lost.'
            else:
                name_str = self.winner.name
                if name_str == '':
                    name_str = 'You'
                text_str += f' {name_str} Won!'
            text = self.font_over.render(text_str, True, self.text_color)
            b = self.get_box()
            self.screen.blit(text, ((b.width-text.get_width())//2, (b.height-45-text.get_height())//2))
            text_str = 'Press ESC or the'
            text = self.font_over.render(text_str, True, self.text_color)
            self.screen.blit(text, ((b.width-text.get_width())//2, (b.height-text.get_height())//2))
            text_str = 'top right corner to restart.'
            text = self.font_over.render(text_str, True, self.text_color)
            self.screen.blit(text, ((b.width-text.get_width())//2, (b.height+45-text.get_height())//2))


    async def run(self):

        self.clock = pygame.time.Clock()

        # Copy initial items to allow reset
        self.init_items = {}
        for i in self.items.keys():
            self.init_items[i] = copy.copy(self.items[i])

        # Game loop
        running = True
        while running:
            # try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.FINGERDOWN:
                    self.finger_pos[event.finger_id] = [int(event.x*self.screen_size[0]), int(event.y*self.screen_size[1])]
                elif event.type == pygame.FINGERMOTION:
                    self.finger_pos[event.finger_id] = [int(event.x*self.screen_size[0]), int(event.y*self.screen_size[1])]
                elif event.type == pygame.FINGERUP:
                    self.finger_pos.pop(event.finger_id,None)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_pressed = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_pos = None
                    self.mouse_pressed = False

            # deal with key presses
            self.keys      = pygame.key.get_pressed()
            if self.mouse_pressed:
                if len(self.finger_pos.keys())==0:
                    self.mouse_pos = pygame.mouse.get_pos()

            self.update()
            for i in self.items.values():
                for j in i:
                    j.update()

            # Drawing
            self.screen.fill(self.background_color)
            if self.draw_fcn is not None:
                self.draw_fcn(self)

            if 'touch' in self.items:
                for j in self.items['touch']:
                    j.draw()
            for i in self.items.keys():
                if i == 'touch' or i == 'player':
                    continue
                for j in self.items[i]:
                    j.draw()
            if 'player' in self.items:
                for j in self.items['player']:
                    j.draw()

            self.draw_text()

            self.counter += 1
            if self.counter == 10000000:
                self.counter = 0
            pygame.display.flip()
            self.clock.tick(self.fps) #Limit framerate to 200 FPS
            await asyncio.sleep(0)
            # except Exception as e:
            #     self.exception_message = str(e)


        pygame.quit()

    @staticmethod
    def push_out(r1, r2):
        """Pushes rect1 out of rect2 after a collision."""
        # Determine collision direction
        rect1 = r1.r()
        rect2 = r2.r()
        # Calculate overlap on each axis
        dx = 0
        dy = 0
        if rect1.centerx < rect2.centerx:
            dx = rect2.left - rect1.right
        else:
            dx = rect2.right - rect1.left
        if rect1.centery < rect2.centery:
            dy = rect2.top - rect1.bottom
        else:
            dy = rect2.bottom - rect1.top

        # Move along the axis with minimum overlap
        if abs(dx) == abs(dy):
            rect1.x += dx
            rect1.y += dy
            r1.x = float(rect1.x)
            r1.y = float(rect1.y)
            return [dx, dy]
        elif abs(dx) < abs(dy):
            rect1.x += dx
            r1.x = float(rect1.x)
            return [dx,0]
        else:
            rect1.y += dy
            r1.y = float(rect1.y)
            return [0, dy]

    @staticmethod
    def hold(c, b):
        if isinstance(b, Item):
            b = b.rect
        GameFixedLevel.push_out(c.rect, b)

    @staticmethod
    def bounce(c, b):
        if isinstance(b, Item):
            b = b.rect
        direction = GameFixedLevel.push_out(c.rect, b)
        if direction[0] != 0:
            c.velocity[0] *= -1
        if direction[1] != 0:
            c.velocity[1] *= -1

    @staticmethod
    def kill_both(c, b):
        if isinstance(b, Item):
            b.live_lost()
        c.live_lost()

    @staticmethod
    def kill_target(c, b):
        if isinstance(b, Item):
            b.live_lost()

    @staticmethod
    def kill_target_and_score(c, b):
        if isinstance(b, Item):
            b.live_lost()
        c.score += 1

    @staticmethod
    def kill_target_and_bounce(c, b):
        GameFixedLevel.bounce(c, b)
        GameFixedLevel.kill_target(c, b)

    @staticmethod
    def kill_me(c, b):
        c.live_lost()

    @staticmethod
    def map_to_key(me, key):
        me.player.do_action(me.key)

    @staticmethod
    def draw_touchpad(surface, color, rect):
        pygame.draw.ellipse(surface, color, rect, width=rect.width*2//6)

    @staticmethod
    def draw_nothing(surface, color, rect):
        pass

    @staticmethod
    def call_reset(me,key):
        me.player.do_reset = True

    def get_starting_pos(self, loc, pad_size):
        x_start = 0
        y_start = 0
        if isinstance(loc[0],str):
            if loc[0] == 'top':
                y_start = 0
            elif loc[0] == 'bottom':
                y_start = self.screen_size[1] - pad_size[1]
        else:
            x_start = loc[0]
        if isinstance(loc[1],str):
            if loc[1] == 'left':
                x_start = 0
            elif loc[1] == 'right':
                x_start = self.screen_size[0] - pad_size[0]
        else:
            x_start = loc[1]
        return [x_start,y_start]


    def create_move_touchpad(self, player, pad_size=(200, 200), loc=('bottom', 'right'), keys='LUDR',color=(60, 60, 60)):
        x_start,y_start = self.get_starting_pos(loc,pad_size)
        tkey = [pygame.K_LEFT, pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT]
        if keys == 'LUDR':
            tname = ['left', 'up', 'down', 'right']
        else:
            tkey = keys
            tname = ['','','','']

        tdx      = [0 , 50,  50, 100]
        tdy      = [50, 0 , 100,  50]
        for i in range(len(tname)):
            t = Item(self, name=tname[i], kind='touch', size=[pad_size[0] // 2, pad_size[1] // 2],
                     init_loc=[x_start + tdx[i], y_start + tdy[i]], draw_fcn=GameFixedLevel.draw_nothing,
                     moves={'touched': GameFixedLevel.map_to_key},
                     color=(0, 0, 0))
            t.player = player
            t.key    = tkey[i]

        t = Item(self, name='draw', kind='touch', size=pad_size,
                 init_loc=[x_start, y_start],
                 draw_fcn=GameFixedLevel.draw_touchpad,
                 color=color)

    def create_key_touchpad(self, player, pad_size=(200, 200), loc=('bottom', 'left'), key=pygame.K_ESCAPE,color=(60, 60, 60)):
        x_start, y_start = self.get_starting_pos(loc, pad_size)
        t = Item(self, name='', kind='touch', size=pad_size,
                 init_loc=[x_start,y_start], draw_fcn=GameFixedLevel.draw_touchpad,
                 moves={'touched': GameFixedLevel.map_to_key},
                 color=color)
        t.player = player
        t.key    = key

    def create_escape_touchpad(self, pad_size=(100, 100), loc=('top', 'right')):
        x_start, y_start = self.get_starting_pos(loc, pad_size)
        t = Item(self, name='escape', kind='touch', size=pad_size,
                 init_loc=[x_start,y_start], draw_fcn=GameFixedLevel.draw_nothing,
                 moves={'touched': GameFixedLevel.call_reset})
        t.player = self

class Item:
    def __init__(self, parent, size, name='', kind='', init_loc=None, velocity=None, draw_fcn=pygame.draw.rect,
                 adv_draw_fcn=None,
                 color=(255, 255, 255), always=None, moves=None, collides=None, box=None, lives=1,
                 live_lost_invincibility=0, live_lost_color=None, live_lost_fcn=None, image_bmp=None,
                 image_inv_bmp=None, reset_fcn=None):

        self.parent    = parent
        self.size      = size
        self.name      = name
        self.kind      = kind

        if init_loc is None:
            init_loc = [0, 0]
        self.init_loc  = init_loc

        if velocity is None:
            velocity = [0, 0]
        self.init_vel  = velocity

        self.draw_fcn  = draw_fcn
        self.adv_draw_fcn = adv_draw_fcn
        self.color     = color
        self.always    = always
        self.moves     = moves

        self.init_box  = box

        if moves is None:
            moves = {}
        self.moves     = moves

        if collides is None:
            collides = {}
        self.collides= collides

        self.init_lives = lives

        self.image_bmp     = image_bmp
        self.image_inv_bmp = image_inv_bmp
        self.reset_fcn     = reset_fcn

        self.parent.add_item(self)
        self.live_lost_invincibility = live_lost_invincibility
        self.live_lost_color = live_lost_color
        if self.live_lost_color is None:
            self.live_lost_color = (self.color[0]//2,self.color[1]//2,self.color[2]//2)
        self.live_lost_fcn = live_lost_fcn

        self.reset()

    def reset(self):
        self.rect = GameRect(self.init_loc[0], self.init_loc[1], self.size[0], self.size[1])

        self.velocity  = self.init_vel
        self.lives     = self.init_lives
        self.image     = None
        if self.image_bmp is not None:
            self.image = pygame.image.load(self.image_bmp)
        self.image_inv  = None
        if self.image_inv_bmp is not None:
            self.image_inv = pygame.image.load(self.image_inv_bmp)

        self.score      = 0
        self.invincible = 0
        self.pause      = 0

        if self.init_box is None:
            self.box = self.parent.get_box()
        else:
            self.box = pygame.Rect(*self.init_box)

        if self.reset_fcn is not None:
            self.reset_fcn(self)

    def get_box(self):
        return self.box


    def draw(self):
        if self.invincible==0 and (self.pause//5)%2==0:
            if self.adv_draw_fcn is not None:
                self.adv_draw_fcn(self,False)
            elif self.image is not None:
                self.parent.screen.blit(self.image, self.rect.r())
            else:
                self.draw_fcn(self.parent.screen, self.color, self.rect.r())
        else:
            if (self.parent.counter//5)%2==0:
                if self.adv_draw_fcn is not None:
                    self.adv_draw_fcn(self,True)
                elif self.image_inv is not None:
                    self.parent.screen.blit(self.image_inv, self.rect.r())
                else:
                    self.draw_fcn(self.parent.screen, self.live_lost_color, self.rect.r())

    def live_lost(self):
        if self.invincible ==0:
            do_usual = True
            if self.live_lost_fcn is not None:
                do_usual = self.live_lost_fcn(self)
            if do_usual:
                self.lives -= 1
                if self.lives==0:
                    if self.kind !='player':
                        self.parent.remove_item(self)
                    else:
                        self.pause = -1
                else:
                    self.invincible = self.live_lost_invincibility

    def add_to_var(self,var,value):
        curr = getattr(self, var)
        if isinstance(curr,list):
            for i in range(len(curr)):
                curr[i] += value[i]
        else:
            curr += value

    def mult_to_var(self,var,value):
        curr = getattr(self, var)
        if isinstance(curr,list):
            for i in range(len(curr)):
                curr[i] *= value[i]
        else:
            curr *= value

    def perform_wrap(self,side,ix):
        if side == 'left':
            self.rect.x = self.parent.screen_size[0] - self.rect.width
        elif side == 'right':
            self.rect.x = 0
        elif side == 'top':
            self.rect.y = self.parent.screen_size[1] - self.rect.height
        elif side == 'bottom':
            self.rect.y = 0

    def do_boundary(self, cond, side, ix):
        if cond and side in self.collides:
            collides_fcn = self.collides[side]
            if  collides_fcn == 'bounce':
                self.rect.clamp_ip(self.get_box())
                self.velocity[ix] *= -1
            elif collides_fcn == 'wrap':
                self.perform_wrap(side,ix)
            elif collides_fcn == 'kill':
                self.live_lost()
            elif callable(collides_fcn):
                collides_fcn(self, self.get_box())
            return True
        return False

    def update(self):

        if self.invincible >0:
            self.invincible -=1

        if self.pause != 0:
            self.pause -= 1
            return

        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        # Key actions
        if self.always is not None:
            self.always(self)
        for i in self.moves.keys():
            if i == 'touched':
                for f in self.parent.finger_pos.keys():
                    if self.parent.finger_pos[f] is not None and self.rect.r().collidepoint(self.parent.finger_pos[f]):
                        self.do_action('touched')
                if self.parent.mouse_pos is not None and self.rect.r().collidepoint(self.parent.mouse_pos):
                    self.do_action('touched')
            elif self.parent.keys[i]:
                self.do_action(i)

        # Collision with the bounds
        r = self.rect.r()
        if not self.do_boundary(r.top <= self.box.top      , 'top'   , 1):
            if not self.do_boundary(r.bottom >= self.box.bottom, 'bottom', 1):
                if not self.do_boundary(r.left <= self.box.left    , 'left'  , 0):
                    self.do_boundary(r.right >= self.box.right  , 'right' , 0)

        # Collision with other items
        for kind in self.collides.keys():
            if kind not in ['top','bottom','left','right','box_fit']:
                item = self.check_if_collides_with(self.rect,kind)
                if item is not None:
                    collides_fcn = self.collides[kind]
                    collides_fcn(self,item)

        if 'box_fit' in self.collides:
            collides_fcn = self.collides['box_fit']
            if collides_fcn == 'hold':
                self.rect.clamp_ip(self.box)
            elif collides_fcn == 'kill':
                if not self.rect.r().colliderect(self.box):
                    self.live_lost()
            else:
                collides_fcn(self, self.box)

    def do_action(self, event):
        if event in self.moves:
            key_action = self.moves[event]
            if isinstance(key_action, list):
                self.rect.x += key_action[0]
                self.rect.y += key_action[1]
            elif callable(key_action):
                key_action(self, event)

    def check_if_collides_with(self,rect,item_kind):
        # Collision with other items
        for i in self.parent.items[item_kind]:
            if rect.r().colliderect(i.rect.r()):
                return i
        return None

