
# this file is used to create the pygbag web.zip file to upload game to itch.io. This used the game.tmpl file.
# to use this file, please comment out asyncio.run(main()) in the file being included.
# e.g. if you are building g1_pong, please go to g1_pong and comment out the asyncio.run(main()) line at the bottom

import asyncio
import pygame
import pygame.freetype
import numpy as np
import random

#from g1_pong import *
#from g2_bricks import *
#from g3_frogger import *
#from g4_space_invaders import *
#from g5_pacman import *
from g6_snake import *

asyncio.run(main())
