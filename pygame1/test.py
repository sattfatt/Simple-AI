import pygame, sys
from pygame.locals import *
from pygame import gfxdraw
import numpy as np
import math

# main


MAXDISPX = 500
MAXDISPY = 400

pygame.init()

DISPLAYSURF = pygame.display.set_mode((MAXDISPX,MAXDISPY), 0, 32)

pygame.display.set_caption('Animation')

FPS = 144
fpsClock = pygame.time.Clock()

# ------------- #
#     events    #
# ------------- #

MOVELEFT  = 97
MOVERIGHT = 100
MOVEUP    = 119
MOVEDOWN  = 115

MOVESPEED = 1
PROJVEL   = 3

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

        self.dir = float(dir)

        self.cursorangle = 0

        self.size = size

        self.color = color

        self.SURFACE = surf

        self.speedMag = PROJVEL

        self.speed = (float(self.speedMag*math.cos(self.dir)),
                      float(self.speedMag*math.sin(self.dir)))

    def spawn(self):
        pygame.gfxdraw.filled_circle(self.SURFACE,
                                     np.round(self.pos[0]).astype(int),
                                     np.round(self.pos[1]).astype(int),
                                     self.size,
                                     self.color)

    def updatePos(self, dpos):
        pos = (self.pos + np.round(dpos)).astype(int)
        pygame.gfxdraw.filled_circle(self.SURFACE, pos[0], pos[1], self.size, self.color)
        self.pos = pos

    def updateProjectile(self):
        self.pos = (self.pos + self.speed)

    def updateDir(self, dir):
        self.dir = dir

    def getCursorAngle(self):
        mousepos = np.array(pygame.mouse.get_pos())
        heading = mousepos - self.pos
        print heading
        return math.atan2(heading[1], heading[0])

def removeCondition(entity):
    if entity.pos[0] <= 0 or entity.pos[1] <= 0 or entity.pos[0] >= MAXDISPX or entity.pos[1] >= MAXDISPY:
        return False
    else:
        return True

# ------------- #
#      main     #
# ------------- #

bob = Entity((200,200), 1, 15, RED, DISPLAYSURF)

projectiles = []


hitboxes = []


prevkey = 0
hold = False

while True:
    DISPLAYSURF.fill(WHITE)

    # event handling
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
        if event.type == MOUSEBUTTONDOWN:
            angle = bob.getCursorAngle()
            print angle
            projectiles.append(Entity((bob.pos[0], bob.pos[1]), angle, 5, BLACK, DISPLAYSURF))

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

    # projectile handling
    if projectiles:
        #print('Projectile(s) Present!')

        for proj in projectiles:

            proj.updateProjectile()

            proj.spawn()
        # remove projectile from list if remove condition is met.
        projectiles[:] = [x for x in projectiles if removeCondition(x)]
    # entity handling
    bob.spawn()

    pygame.display.update()
    fpsClock.tick(FPS)

