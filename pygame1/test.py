import pygame, sys
from pygame.locals import *
from pygame import gfxdraw
import numpy as np
import math

# main
pygame.init()
pygame.display.set_caption('Animation')
FPS = 120
fpsClock = pygame.time.Clock()

# ------------- #
#     events    #
# ------------- #

MOVELEFT = 97
MOVERIGHT = 100
MOVEUP = 119
MOVEDOWN = 115

# ------------- #
#    params     #
# ------------- #

MAXHEALTH = 100
MOVESPEED = 1
PROJVEL = 5
MAXSPINRATE = 2
PROJECTILEINTERVAL = 15
MAXNEURONSPERLAYER = 10
MAXDISPX = 1500  # 1024
MAXDISPY = 1000  # 768
MINRANDPARM = -10000
MAXRANDPARM = 10000

# ------------- #
#     colors    #
# ------------- #

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)

# ------------- #
#    surface    #
# ------------- #


DISPLAYSURF = pygame.display.set_mode((MAXDISPX, MAXDISPY), 0, 32)

DISPLAYRECT = pygame.Rect(0, 0, MAXDISPX, MAXDISPY)

DISPLAYSURF.fill(BLACK)
# ------------- #
#   Classes     #
# ------------- #


class Entity:
    def __init__(self, pos, dir, size, color, surf, owner):

        self.projectileint = 0

        self.clock = pygame.time.Clock()

        self.health = MAXHEALTH

        self.prevpos = (0, 0)

        self.hit = False

        self.collisioncount = 0

        self.size = size

        self.wedgeMag = 1000

        self.owner = owner

        self.pov = 20

        self.pos = np.asarray(pos)

        self.detectEnemy = False

        self.truepos = self.pos.astype(float)

        self.dir = dir

        self.cursorangle = 0

        self.size = size

        self.color = color

        self.SURFACE = surf

        self.speedMag = PROJVEL

        self.speed = (float(self.speedMag * math.cos(math.radians(self.dir))),
                      float(self.speedMag * math.sin(math.radians(self.dir))))

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

        pos = np.round(self.truepos + (dpos[0] * MOVESPEED, dpos[1] * MOVESPEED)).astype(int)

        if DISPLAYRECT.collidepoint(pos[0], pos[1]):
            self.pos = pos
            self.truepos += (dpos[0] * MOVESPEED, dpos[1] * MOVESPEED)
            # pygame.gfxdraw.filled_circle(self.SURFACE, pos[0], pos[1], self.size, self.color)

    def updateProjectile(self):
        self.pos = (self.pos + self.speed)

    def getCursorAngle(self):
        mousepos = np.array(pygame.mouse.get_pos())
        heading = mousepos - self.pos
        # print heading
        return math.degrees(math.atan2(heading[1], heading[0]))

    def drawWedge(self):
        # creates wedge with variable pov
        pov = math.radians(self.pov)
        dir = math.radians(self.dir)
        # self.dir = self.getCursorAngle()
        endpointupper = (self.wedgeMag * math.cos(pov / 2 + dir) + self.pos[0],
                         self.wedgeMag * math.sin(pov / 2 + dir) + self.pos[1])
        endpointlower = (self.wedgeMag * math.cos(-(pov / 2) + dir) + self.pos[0],
                         self.wedgeMag * math.sin(-(pov / 2) + dir) + self.pos[1])
        pygame.draw.aaline(DISPLAYSURF, CYAN, self.pos, (endpointupper[0], endpointupper[1]), 1)
        pygame.draw.aaline(DISPLAYSURF, CYAN, self.pos, (endpointlower[0], endpointlower[1]), 1)

    def updateHitbox(self):
        self.hitbox = pygame.Rect(self.pos[0] - self.size, self.pos[1] - self.size, self.size * 2, self.size * 2)

    def drawHitbox(self):
        pygame.draw.rect(DISPLAYSURF, GREEN, self.hitbox, 2)

    def collisionDetection(self, entity):
        '''indicates whether the projectile hit and should be deleted. Also modifies the health of target'''

        if self.hitbox.colliderect(entity.hitbox) and self.owner != entity.owner:
            entity.collisioncount += 1
            entity.health -= 10
            print(entity.owner + ' was hit by ' + self.owner + ' ' + str(
                entity.collisioncount) + ' time(s).' + ' Health: ' + str(entity.health))
            self.hit = True

    def inWedge(self, projectile):
        '''returns  projectile owner in the FOV.
        just check the argument of the projectile relative to the self'''

        relativepos = projectile.pos - self.pos
        argument = math.atan2(relativepos[1], relativepos[0])
        arg = math.degrees(argument) + (360 * math.floor(self.dir / 360))
        # print(arg)
        if (self.dir + self.pov / 2) >= arg >= (self.dir - self.pov / 2) and projectile.owner != self.owner:
            self.detectEnemy = True
            return True
        else:
            self.detectEnemy = False
            return False

    def control(self, controlframe):
        ''' Based on the control frame input, the entity will be moved and/or rotated '''
        self.updatePos(controlframe.deltaDirection)
        self.dir += controlframe.deltaHeading

    def state(self):

        return (self.pos[0], self.pos[1], self.dir, self.detectEnemy, self.health)


class ControlFrame:
    def __init__(self, id):
        self.deltaHeading = 0
        self.deltaDirection = (0, 0)
        self.fire = False
        self.id = id


def removeCondition(entity):
    if entity.pos[0] <= 0 or entity.pos[1] <= 0 or entity.pos[0] >= MAXDISPX or entity.pos[1] >= MAXDISPY or entity.hit:
        return False
    else:
        return True


class NN(ControlFrame):
    ''' NN with weights chosen by GA'''

    def __init__(self, owner):
        ControlFrame.__init__(self, owner)
        # initialize weights and biases with gaussian N(0,1) random values
        self.w1 = np.array(np.random.randint(MINRANDPARM, MAXRANDPARM, (MAXNEURONSPERLAYER, 5)))
        self.b1 = np.array(np.random.randint(MINRANDPARM, MAXRANDPARM, (MAXNEURONSPERLAYER,)))
        self.w2 = np.array(np.random.randint(MINRANDPARM, MAXRANDPARM, (MAXNEURONSPERLAYER, MAXNEURONSPERLAYER)))
        self.b2 = np.array(np.random.randint(MINRANDPARM, MAXRANDPARM, (MAXNEURONSPERLAYER,)))
        self.w3 = np.array(np.random.randint(MINRANDPARM, MAXRANDPARM, (5, MAXNEURONSPERLAYER)))
        self.b3 = np.array(np.random.randint(MINRANDPARM, MAXRANDPARM, (5,)))

        self.score = 0

    def out(self, input):
        # output
        # -              -
        # |   delta X    |
        # |   delta Y    |
        # | delta Angle  |
        # | Fire boolean |
        # -              -
        #
        layer1Out = np.tanh(self.w1 @ np.asarray(input) + self.b1)

        layer2Out = np.tanh(self.w2 @ np.asarray(layer1Out) + self.b2)

        preIndicator = (self.w3 @ layer2Out) + self.b3

        finalLayerOut = (np.tanh(preIndicator[0]),
                         np.tanh(preIndicator[1]),
                         np.tanh(preIndicator[2]),
                         np.piecewise(preIndicator[3], [preIndicator[3] < 0, preIndicator[3] >= 0], [0, 1]))

        ControlFrame.deltaDirection = (finalLayerOut[0], finalLayerOut[1])
        ControlFrame.deltaHeading = finalLayerOut[2] * MAXSPINRATE
        ControlFrame.fire = finalLayerOut[3]

        return ControlFrame

    def updateWeights(self):
        pass


def breed(NN1, NN2, owner):
    '''Takes in two NN's and outputs a child with randomly chosen Neuron weight clusters from both'''
    baby = NN(owner)

    for row in range(MAXNEURONSPERLAYER):
        choice = np.random.binomial(1, 0.5)
        if choice:
            baby.w1[row, :] = NN1.w1[np.random.randint(0, MAXNEURONSPERLAYER), :]
            # yes may get same weights for multiple neurons....
        else:
            baby.w1[row, :] = NN2.w1[np.random.randint(0, MAXNEURONSPERLAYER), :]

    for row in range(MAXNEURONSPERLAYER):
        choice = np.random.binomial(1, 0.5)
        if choice:
            baby.w2[row, :] = NN1.w2[np.random.randint(0, MAXNEURONSPERLAYER), :]
            # yes may get same weights for multiple neurons....
        else:
            baby.w2[row, :] = NN2.w2[np.random.randint(0, MAXNEURONSPERLAYER), :]

    for row in range(5):
        choice = np.random.binomial(1, 0.5)
        if choice:
            baby.w3[row, :] = NN1.w3[np.random.randint(0, 5), :]
            # yes may get same weights for multiple neurons....
        else:
            baby.w3[row, :] = NN2.w3[np.random.randint(0, 5), :]

    for weight in range(MAXNEURONSPERLAYER):
        choice = np.random.binomial(1, 0.5)
        if choice:
            baby.b1[weight] = NN1.b1[np.random.randint(0, MAXNEURONSPERLAYER)]
        else:
            baby.b1[weight] = NN2.b1[np.random.randint(0, MAXNEURONSPERLAYER)]

    for weight in range(MAXNEURONSPERLAYER):
        choice = np.random.binomial(1, 0.5)
        if choice:
            baby.b2[weight] = NN1.b2[np.random.randint(0, MAXNEURONSPERLAYER)]
        else:
            baby.b2[weight] = NN2.b2[np.random.randint(0, MAXNEURONSPERLAYER)]

    for weight in range(5):
        choice = np.random.binomial(1, 0.5)
        if choice:
            baby.b3[weight] = NN1.b3[np.random.randint(0, 5)]
        else:
            baby.b3[weight] = NN2.b3[np.random.randint(0, 5)]

    return baby


# ------------- #
#      main     #
# ------------- #

# create 10 random NNs for each AI

NNlist1 = [NN('bob'), NN('bob'), NN('bob'), NN('bob'), NN('bob'), NN('bob'), NN('bob'), NN('bob'), NN('bob'), NN('bob')]

NNlist2 = [NN('joe'), NN('joe'), NN('joe'), NN('joe'), NN('joe'), NN('joe'), NN('joe'), NN('joe'), NN('joe'), NN('joe')]

bob = Entity((np.random.randint(1, MAXDISPX - 1), np.random.randint(1, MAXDISPY - 1)), 0, 15, RED, DISPLAYSURF, 'bob')
joe = Entity((np.random.randint(1, MAXDISPX - 1), np.random.randint(1, MAXDISPY - 1)), 0, 15, RED, DISPLAYSURF, 'joe')

# start with the first of 10 nets
nets = [NNlist1[0], NNlist2[0]]

projectiles = []

entities = [bob, joe]

testbaby = breed(NNlist1[0], NNlist2[0], 'bob')

while True:

    DISPLAYSURF.fill(BLACK)
    # movement
    keys = pygame.key.get_pressed()
    if keys[K_a]:
        prevkey = MOVELEFT
        # print('left event')
        entities[0].updatePos(np.array([-MOVESPEED, 0]))
    if keys[K_d]:
        prevkey = MOVERIGHT
        # print('right event')
        entities[0].updatePos(np.array([MOVESPEED, 0]))
    if keys[K_w]:
        prevkey = MOVEUP
        # print('up event')
        entities[0].updatePos(np.array([0, -MOVESPEED]))
    if keys[K_s]:
        prevkey = MOVEDOWN
        # print('down event')
        entities[0].updatePos(np.array([0, MOVESPEED]))
        # if keys[K_s] and keys[K_d]:
        #   bob.updatePos(np.array([MOVESPEED, MOVESPEED]))

    # event handling
    for event in pygame.event.get():

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                angle = entities[0].getCursorAngle()
                # print angle
                projectiles.append(
                    Entity((entities[0].pos[0], entities[0].pos[1]), angle, 5, WHITE, DISPLAYSURF, entities[0].owner))
            if event.key == K_l:
                pass

    # projectile handling
    if projectiles:
        # print('Projectile(s) Present!')

        for proj in projectiles:
            proj.updateProjectile()

            proj.draw()
            # print(proj.pos)
            # for entity in entities:
            #    proj.collisionDetection(entity)
            #    temp = entity.inWedge(proj)
            #    if temp:
            #        counter += 1
            # ----DEBUG----#
            # print counter
            # print('checking: ' + entity.owner)
            # print(temp + '\'s projectile is in ' + entity.owner + '\'s FOV')

        # remove projectile from list if remove condition is met.
        projectiles[:] = [x for x in projectiles if removeCondition(x)]

        # entity handling
    #    entities[0].dir = entities[0].getCursorAngle()
    if entities:
        for entity in entities:
            entity.draw()
            entity.drawWedge()
            for players in entities:
                if players != entity:
                    if (entity.inWedge(players)):
                        print(entity.owner + ' detects ' + players.owner)

            # create list of NNs for each entity
            nextmove = nets[entities.index(entity)].out(entity.state())
            # print(str(nextmove.deltaDirection) + " " + str(nextmove.deltaHeading) + " " + str(nextmove.fire))
            entity.control(nextmove)
            entity.projectileint += 1
            if nextmove.fire and entity.projectileint >= PROJECTILEINTERVAL:
                entity.projectileint = 0
                projectiles.append(
                    Entity((entity.pos[0], entity.pos[1]), entity.dir, 5, WHITE, DISPLAYSURF, entity.owner))
        entities[:] = [x for x in entities if not x.health == 0]

    pygame.display.update()
    fpsClock.tick(FPS)
