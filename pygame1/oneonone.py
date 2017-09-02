import pygame, sys
from pygame.locals import *
from pygame import gfxdraw
import numpy as np
import math
import random

# main
pygame.init()
pygame.font.init()
pygame.display.set_caption('Animation')
FPS = 1000
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
MAXITERATIONS = 10000
MAXHEALTH = 1000
MOVESPEED = 1
PROJVEL = 3
MAXSPINRATE = 1
PROJECTILEINTERVAL = 500
MAXNEURONSPERLAYER = 5
MAXDISPX = 1918  # 1024
MAXDISPY = 1005  # 768
MINRANDPARM = -1
MAXRANDPARM = 1
POPULATION = 20

# ------------- #
#    Globals    #
# ------------- #

iteration = 0

tick = 0

popindex = 0

generation = 0

displayupdateinterval = 10

runnormal = False


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

        self.endpointupper = (0, 0)

        self.endpointlower = (0, 0)

        self.damagedealt = 0

        self.projectileint = 0

        self.clock = pygame.time.Clock()

        self.health = MAXHEALTH

        self.prevpos = (0, 0)

        self.hit = False

        self.collisioncount = 0

        self.size = size

        self.wedgeMag = 1000

        self.owner = owner

        self.fov = 5

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
        #pygame.gfxdraw.filled_circle(self.SURFACE,
                                     #np.round(self.pos[0]).astype(int),
                                     #np.round(self.pos[1]).astype(int),
                                     #self.size,
                                     #self.color)

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

    def iniWedge(self, display=True):
        # creates wedge with variable pov
        pov = math.radians(self.fov)
        dir = math.radians(self.dir)
        # self.dir = self.getCursorAngle()
        self.endpointupper = (self.wedgeMag * math.cos(pov / 2 + dir) + self.pos[0],
                              self.wedgeMag * math.sin(pov / 2 + dir) + self.pos[1])
        self.endpointlower = (self.wedgeMag * math.cos(-(pov / 2) + dir) + self.pos[0],
                              self.wedgeMag * math.sin(-(pov / 2) + dir) + self.pos[1])
        if display:
            pass
            #pygame.draw.aaline(DISPLAYSURF, WHITE, self.pos, (self.endpointupper[0], self.endpointupper[1]), 1)
            #pygame.draw.aaline(DISPLAYSURF, WHITE, self.pos, (self.endpointlower[0], self.endpointlower[1]), 1)

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
        else:
            self.hit = False

    def inWedge(self, projectile):
        '''returns  projectile owner in the FOV.
        use triangle technique so we don't have to deal with unnormalized angles'''

        # compute necessary vectors:
        v0 = (self.endpointlower - self.pos)
        v1 = (self.endpointupper - self.pos)
        v2 = (projectile.pos - self.pos)

        # calculate dot products
        s00 = np.inner(v0, v0)
        s01 = np.inner(v0, v1)
        s02 = np.inner(v0, v2)
        s11 = np.inner(v1, v1)
        s12 = np.inner(v1, v2)

        # calculate barycentric points
        scalar = 1 / (s00 * s11 - s01 * s01)
        u = (s11 * s02 - s01 * s12) * scalar
        v = (s00 * s12 - s01 * s02) * scalar

        if u >= 0 and v >= 0 and self.owner != projectile.owner:
            self.detectEnemy = True
            # print(self.owner + ' detects enemy!')
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

    def reset(self):
        self.health = MAXHEALTH


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
        self.w1 = np.array(np.random.uniform(MINRANDPARM, MAXRANDPARM, (MAXNEURONSPERLAYER, 5)))
        self.b1 = np.array(np.random.uniform(MINRANDPARM, MAXRANDPARM, (MAXNEURONSPERLAYER,)))
        self.w2 = np.array(np.random.uniform(MINRANDPARM, MAXRANDPARM, (MAXNEURONSPERLAYER, MAXNEURONSPERLAYER)))
        self.b2 = np.array(np.random.uniform(MINRANDPARM, MAXRANDPARM, (MAXNEURONSPERLAYER,)))
        self.w3 = np.array(np.random.uniform(MINRANDPARM, MAXRANDPARM, (5, MAXNEURONSPERLAYER)))
        self.b3 = np.array(np.random.uniform(MINRANDPARM, MAXRANDPARM, (5,)))

        self.score = 0

        self.probability = 0

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


def getScore(NN):
    return NN.score


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


def mutate(NN):
    """currently mutates all weight clusters (rows) using normal distribution centered at the clusters"""
    # weights
    for row in range(MAXNEURONSPERLAYER):
        NN.w1[row, :] = np.random.multivariate_normal(NN.w1[row, :], np.identity(len(NN.w1[row, :])))
        NN.w2[row, :] = np.random.multivariate_normal(NN.w2[row, :], np.identity(len(NN.w2[row, :])))
    for row in range(5):
        NN.w3[row, :] = np.random.multivariate_normal(NN.w3[row, :], np.identity(len(NN.w3[row, :])))
    # biases
    NN.b1 = np.random.multivariate_normal(NN.b1, np.identity(len(NN.b1)))
    NN.b2 = np.random.multivariate_normal(NN.b2, np.identity(len(NN.b2)))
    NN.b3 = np.random.multivariate_normal(NN.b3, np.identity(len(NN.b3)))

    return NN


def setScore(NN):
    pass


def rouletteWheel(NNlist, n=1):
    totalfitness = 0
    offset = 0
    selected = []
    for i in range(len(NNlist)):
        totalfitness += NNlist[i].score

    if totalfitness == 0:
        totalfitness = 1

    for brain in NNlist:
        brain.probability = offset + brain.score / totalfitness
        offset += brain.probability

    selected = []
    for i in range(n):
        r = random.random()
        selected.append(NNlist[0])
        for brain in NNlist:
            if brain.probability > r:
                break
            try:
                selected[i] = brain
            except IndexError:
                selected.append(brain)
    return selected


def newGen(NNlist):
    children = []
    fittest = rouletteWheel(NNlist, 2)
    for net in NNlist:
        children.append(mutate(breed(fittest[0], fittest[1], NNlist[0].id)))
    return children


# ------------- #
#      main     #
# ------------- #

# create 10 random NNs for each AI

NNlist1 = []
NNlist2 = []

for i in range(POPULATION):
    NNlist1.append(NN('bob'))
    NNlist2.append(NN('joe'))

bob = Entity((np.random.randint(1, MAXDISPX - 1), np.random.randint(1, MAXDISPY - 1)), 0, 15, RED, DISPLAYSURF, 'bob')
joe = Entity((np.random.randint(1, MAXDISPX - 1), np.random.randint(1, MAXDISPY - 1)), 0, 15, CYAN, DISPLAYSURF, 'joe')

# start with the first of 10 nets
nets = [NNlist1[0], NNlist2[0]]

projectiles = []

entities = [bob, joe]

testbaby = breed(NNlist1[0], NNlist2[0], 'bob')

keys = []

fontObj = pygame.font.Font(pygame.font.get_default_font(), 30)
textSurf = fontObj.render('Gen: ' + str(generation) + ' Pop: ' + str(popindex), True, WHITE)
textRect = textSurf.get_rect()
textRect.topleft = (10, 10)

while True:
    #DISPLAYSURF.fill(BLACK)


    iteration += 1

    if iteration >= MAXITERATIONS or len(entities) < 2:
        iteration = 0
        popindex += 1
        textSurf = fontObj.render('Gen: ' + str(generation) + ' Pop: ' + str(popindex), True, WHITE)
        if popindex == len(NNlist1):
            print('all nets in population tested!')
            popindex = 0
            print('Breeding new generation...', end='')
            NNlist1 = newGen(NNlist1)
            NNlist2 = newGen(NNlist2)
            generation += 1

            print('respawning entities...', end='')
            joe = Entity((np.random.randint(1, MAXDISPX - 1), np.random.randint(1, MAXDISPY - 1)), 0, 15, CYAN,
                         DISPLAYSURF, 'joe')
            bob = Entity((np.random.randint(1, MAXDISPX - 1), np.random.randint(1, MAXDISPY - 1)), 0, 15, RED,
                         DISPLAYSURF, 'bob')
            entities = [bob, joe]
            projectiles = []
            textSurf = fontObj.render('Gen: ' + str(generation) + ' Pop: ' + str(popindex), True, WHITE)
            print('done!')
            continue

        # set the score for the NNs
        for idx, net in enumerate(nets):
            print('Scoring ' + net.id + '...', end='')
            # score function
            try:
                net.score = entities[idx].damagedealt
            except(IndexError):
                # this means entity died, failure!
                net.score = 0
            print(net.score)

        print('Need to advance in Population')
        # reset bob and joe and and entities list
        print('respawning...', end='')
        joe = Entity((np.random.randint(1, MAXDISPX - 1), np.random.randint(1, MAXDISPY - 1)), 0, 15, CYAN,
                     DISPLAYSURF, 'joe')
        bob = Entity((np.random.randint(1, MAXDISPX - 1), np.random.randint(1, MAXDISPY - 1)), 0, 15, RED,
                     DISPLAYSURF, 'bob')
        entities = [bob, joe]
        print('done')

        nets = [NNlist1[popindex], NNlist2[popindex]]
        projectiles = []

    # keys

    # event handling
    for event in pygame.event.get():

        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_m:
                runnormal = False
                DISPLAYSURF.fill(BLACK)
                pygame.display.update()
            if event.key == K_n:
                runnormal = True

    # projectile handling
    if projectiles:
        # print('Projectile(s) Present!')

        for proj in projectiles:
            proj.updateProjectile()

            proj.draw()
            # print(proj.pos)
            for entity in entities:
                proj.collisionDetection(entity)
                # print(projectiles)
                if proj.hit:
                    if proj.owner == 'bob':
                        bob.damagedealt += 10
                        # print('bob dealt ' + str(bob.damagedealt))
                    elif proj.owner == 'joe':
                        joe.damagedealt += 10
                        # print('joe dealt ' + str(joe.damagedealt))
                    projectiles[:] = [x for x in projectiles if removeCondition(
                        x)]  # for some reason I have to remove the projectile right away in this scope if hit
        # remove projectile from list if remove condition is met.
        projectiles[:] = [x for x in projectiles if removeCondition(x)]

        # entity handling
    #    entities[0].dir = entities[0].getCursorAngle()
    if entities:
        for entity in entities:
            entity.draw()
            entity.iniWedge(True)

            entity.inWedge(entities[0])
            entity.inWedge(entities[1])

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

    if runnormal:
        # draw all things here.
        tick += 1

        if tick >= displayupdateinterval:

            for projectile in projectiles:
                pygame.gfxdraw.filled_circle(projectile.SURFACE,
                                             np.round(projectile.pos[0]).astype(int),
                                             np.round(projectile.pos[1]).astype(int),
                                             projectile.size,
                                             projectile.color)
            for entity in entities:
                pygame.draw.aaline(DISPLAYSURF, WHITE, entity.pos, (entity.endpointupper[0], entity.endpointupper[1]),
                                   1)
                pygame.draw.aaline(DISPLAYSURF, WHITE, entity.pos, (entity.endpointlower[0], entity.endpointlower[1]),
                                   1)
                pygame.gfxdraw.filled_circle(entity.SURFACE,
                                             np.round(entity.pos[0]).astype(int),
                                             np.round(entity.pos[1]).astype(int),
                                             entity.size,
                                             entity.color)


            pygame.display.update()
            DISPLAYSURF.fill(BLACK)
            DISPLAYSURF.blit(textSurf,textRect)
            tick = 0

    #pygame.display.update()
    #pygame.display.update([entities[0].hitbox, entities[1].hitbox])


    #print(fpsClock.tick(0))
