import pygame, sys
from pygame.locals import *
from pygame import gfxdraw
import numpy as np
import math

# main


MAXDISPX = 1024
MAXDISPY = 768

pygame.init()

DISPLAYSURF = pygame.display.set_mode((MAXDISPX,MAXDISPY), 0, 32)

DISPLAYRECT = pygame.Rect(0,0,MAXDISPX,MAXDISPY)

pygame.display.set_caption('Animation')

FPS = 60
fpsClock = pygame.time.Clock()

# ------------- #
#     events    #
# ------------- #

MOVELEFT  = 97
MOVERIGHT = 100
MOVEUP    = 119
MOVEDOWN  = 115

MOVESPEED = 5
PROJVEL   = 15

# ------------- #
#     colors    #
# ------------- #

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)
CYAN  = (  0, 255, 255)

# ------------- #
#    surface    #
# ------------- #

DISPLAYSURF.fill(BLACK)

# ------------- #
#   Classes     #
# ------------- #


class Entity:

    def __init__(self, pos, dir, size, color, surf, owner):
        self.prevpos = (0,0)

        self.hit = False

        self.collisioncount = 0

        self.size = size

        self.wedgeMag = 1000

        self.owner = owner

        self.pov = 0

        self.pos = np.asarray(pos)

        self.dir = float(dir)

        self.cursorangle = 0

        self.size = size

        self.color = color

        self.SURFACE = surf

        self.speedMag = PROJVEL

        self.speed = (float(self.speedMag*math.cos(self.dir)),
                      float(self.speedMag*math.sin(self.dir)))

        self.hitbox = pygame.Rect(self.pos[0] - size, self.pos[1] - size, size, size)

        self.drawhitboxflag = False


    def draw(self):
        pygame.gfxdraw.filled_circle(self.SURFACE,
                                     np.round(self.pos[0]).astype(int),
                                     np.round(self.pos[1]).astype(int),
                                     self.size,
                                     self.color)

        self.updateHitbox()
        if self.drawhitboxflag == True:
            self.drawHitbox()

    def updatePos(self, dpos):

        pos = (self.pos + np.round(dpos)).astype(int)

        if DISPLAYRECT.collidepoint(pos[0], pos[1]):
            self.pos = pos
        #pygame.gfxdraw.filled_circle(self.SURFACE, pos[0], pos[1], self.size, self.color)





    def updateProjectile(self):
        self.pos = (self.pos + self.speed)

    def getCursorAngle(self):
        mousepos = np.array(pygame.mouse.get_pos())
        heading = mousepos - self.pos
        #print heading
        return math.atan2(heading[1], heading[0])

    def drawWedge(self, pov):
        # creates wedge with variable pov
        self.pov = pov
        self.dir = self.getCursorAngle()
        endpointupper = (self.wedgeMag * math.cos(self.pov / 2 + self.dir) + self.pos[0],
                         self.wedgeMag * math.sin(self.pov / 2 + self.dir) + self.pos[1])
        endpointlower = (self.wedgeMag * math.cos(-(self.pov / 2) + self.dir) + self.pos[0],
                         self.wedgeMag * math.sin(-(self.pov / 2) + self.dir) + self.pos[1])
        pygame.draw.aaline(DISPLAYSURF, CYAN, self.pos, (endpointupper[0], endpointupper[1]))
        pygame.draw.aaline(DISPLAYSURF, CYAN, self.pos, (endpointlower[0], endpointlower[1]))

    def updateHitbox(self):
        self.hitbox = pygame.Rect(self.pos[0] - self.size, self.pos[1] - self.size, self.size*2, self.size*2)

    def drawHitbox(self):
        pygame.draw.rect(DISPLAYSURF, GREEN, self.hitbox, 2)

    def collisionDetection(self, entity):
        if self.hitbox.colliderect(entity.hitbox) and self.owner != entity.owner:
            entity.collisioncount += 1
            print(entity.owner + ' was hit by ' + self.owner + ' ' + str(entity.collisioncount) + ' time(s).')
            self.hit = True
        else:
            self.hit = False




def removeCondition(entity):
    if entity.pos[0] <= 0 or entity.pos[1] <= 0 or entity.pos[0] >= MAXDISPX or entity.pos[1] >= MAXDISPY or entity.hit:
        return False
    else:
        return True

# ------------- #
#      main     #
# ------------- #

bob = Entity((200,200), 0, 15, RED, DISPLAYSURF, 'bob')
joe = Entity((200,300), 0, 15, RED, DISPLAYSURF, 'joe')

projectiles = []

hitboxes = []

prevkey = 0

hold = False

while True:
    DISPLAYSURF.fill(BLACK)
    # movement
    keys = pygame.key.get_pressed()
    if keys[K_a]  :
        prevkey = MOVELEFT
        #print('left event')
        bob.updatePos(np.array([-MOVESPEED, 0]))
    if keys[K_d]:
        prevkey = MOVERIGHT
        #print('right event')
        bob.updatePos(np.array([MOVESPEED, 0]))
    if keys[K_w]:
        prevkey = MOVEUP
        #print('up event')
        bob.updatePos(np.array([0, -MOVESPEED]))
    if keys[K_s]:
        prevkey = MOVEDOWN
        #print('down event')
        bob.updatePos(np.array([0, MOVESPEED]))
    #if keys[K_s] and keys[K_d]:
     #   bob.updatePos(np.array([MOVESPEED, MOVESPEED]))

    # event handling
    for event in pygame.event.get():

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                angle = bob.getCursorAngle()
                #print angle
                projectiles.append(Entity((bob.pos[0], bob.pos[1]), angle, 5, WHITE, DISPLAYSURF, 'bob'))

    # projectile handling
    if projectiles:
        #print('Projectile(s) Present!')

        for proj in projectiles:

            proj.updateProjectile()

            proj.draw()
            print(proj.pos)
            proj.collisionDetection(joe)
            #projectiles[:] = [x for x in projectiles if not bob.collisionDetection(proj)]


        # remove projectile from list if remove condition is met.
        projectiles[:] = [x for x in projectiles if removeCondition(x)]

    # entity handling
    bob.draw()
    bob.drawWedge(math.radians(20))
    joe.draw()

    #bob.drawWedge(math.radians(20))

    pygame.display.update()
    fpsClock.tick(FPS)

