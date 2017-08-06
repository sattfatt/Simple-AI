import pygame, sys
from pygame.locals import *
from pygame import gfxdraw
import numpy as np

# main

pygame.init()

DISPLAYSURF = pygame.display.set_mode((500,400), 0, 32)

pygame.display.set_caption('Animation')

FPS = 144
fpsClock = pygame.time.Clock()

# ------------- #
#     events    #
# ------------- #

MOVELEFT = 97
MOVERIGHT = 100
MOVEUP = 119
MOVEDOWN = 115

MOVESPEED = 1
PROJVEL = 5

# ------------- #
#     colors    #
# ------------- #

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)

# ------------- #
#    surface    #
# ------------- #

DISPLAYSURF.fill(WHITE)

# ------------- #
#   Classes     #
# ------------- #


class Entity:
    def __init__(self, pos, dir, size, color, surf):
        self.pos = np.asarray(pos)

        self.dir = dir

        self.size = size

        self.color = color

        self.SURFACE = surf

    def spawn(self):
        pygame.gfxdraw.filled_circle(self.SURFACE, self.pos[0], self.pos[1], self.size, self.color)


    def updatePos(self, dpos):
        pos = (self.pos + np.round(dpos)).astype(int)
        pygame.gfxdraw.filled_circle(self.SURFACE, pos[0], pos[1], self.size, self.color)
        self.pos = pos

        pass

    def updateDir(self, dir):
        self.dir = dir
        pass


# ------------- #
#      main     #
# ------------- #


bob = Entity((200,200), (1, 1), 15, RED, DISPLAYSURF)

projectiles = []

prevkey = 0
hold = False

while True:
    DISPLAYSURF.fill(WHITE)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            hold = True
            print(event.key)
            if event.key == MOVELEFT or (hold & prevkey == MOVELEFT):
                prevkey = MOVELEFT
                print('left event')
                bob.updatePos(np.array([-MOVESPEED,0]))
            if event.key == MOVERIGHT or (hold & prevkey == MOVERIGHT):
                prevkey = MOVERIGHT
                print('left event')
                bob.updatePos(np.array([MOVESPEED,0]))
            if event.key == MOVEUP or (hold & prevkey == MOVEUP):
                prevkey = MOVEUP
                print('left event')
                bob.updatePos(np.array([0,-MOVESPEED]))
            if event.key == MOVEDOWN or (hold & prevkey == MOVEDOWN):
                prevkey = MOVEDOWN
                print('left event')
                bob.updatePos(np.array([0,MOVESPEED]))
        if event.type == KEYUP:
            hold = False
            prevkey = 0

    if hold:
        if prevkey == MOVELEFT or (hold & prevkey == MOVELEFT):
            print('left event hold')
            bob.updatePos(np.array([-MOVESPEED, 0]))
        if prevkey == MOVERIGHT or (hold & prevkey == MOVERIGHT):
            print('left event hold')
            bob.updatePos(np.array([MOVESPEED, 0]))
        if prevkey == MOVEUP or (hold & prevkey == MOVEUP):
            print('left event hold')
            bob.updatePos(np.array([0, -MOVESPEED]))
        if prevkey == MOVEDOWN or (hold & prevkey == MOVEDOWN):
            print('left event hold')
            bob.updatePos(np.array([0, MOVESPEED]))

    if not projectiles:
        for proj in projectiles:

            proj.spawn()

    bob.spawn()

    pygame.display.update()
    fpsClock.tick(FPS)

