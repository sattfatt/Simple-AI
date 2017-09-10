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
np.random.seed(np.random.randint(1, 1000000))
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
MAXHEALTH = 10000
MOVESPEED = 1
PROJVEL = 1
MAXSPINRATE = 1
PROJECTILEINTERVAL = 250
MAXNEURONSPERLAYER = 6
MAXDISPX = 1918  # 1024
MAXDISPY = 1005  # 768
MINRANDPARM = -1
MAXRANDPARM = 1
POPULATION = 10

# ------------- #
#    Globals    #
# ------------- #

iteration = 0

tick = 0

popindex = 0

generation = 0

displayupdateinterval = 10

runnormal = False

keystate = 0

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


DISPLAYSURF = pygame.display.set_mode((MAXDISPX, MAXDISPY))

DISPLAYRECT = pygame.Rect(0, 0, MAXDISPX, MAXDISPY)

DISPLAYSURF.fill(BLACK)

# ------------- #
#     walls     #
# ------------- #

walls = []
bigbox = pygame.Rect(0,0,1,1000)
bigbox.center = (int(math.floor(MAXDISPX/2)),int(math.floor(MAXDISPY/2)))

# ------------- #
#   Classes     #
# ------------- #


class Entity:
    def __init__(self, pos, dir, size, color, surf, owner, type='entity'):
        self.fired = False

        self.hitwall = False

        self.type = type

        self.endpointupper = (0, 0)

        self.endpointlower = (0, 0)

        self.damagedealt = 0

        self.totaldamage = 0

        self.projectileint = 0

        self.clock = pygame.time.Clock()

        self.health = MAXHEALTH

        self.prevdel = (0, 0)

        self.hit = False

        self.collisioncount = 0

        self.size = size

        self.wedgeMag = 1000

        self.owner = owner

        self.fov = 5

        self.pos = np.asarray(pos)

        self.detectEnemy = 0

        self.detectProjectile = 0

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
        self.updateHitbox()
        if self.drawhitboxflag:
            self.drawHitbox()

    def updatePos(self, dpos):

        pos = np.round(self.truepos + (dpos[0] * MOVESPEED, dpos[1] * MOVESPEED)).astype(int)

        if DISPLAYRECT.collidepoint(pos[0], pos[1]):
            self.pos = pos
            self.truepos += (dpos[0] * MOVESPEED, dpos[1] * MOVESPEED)
        if DISPLAYRECT.contains(self.hitbox):
            self.hitwall = False
        else:
            self.hitwall = True
            # print('hitting wall!')

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
            # pygame.draw.aaline(DISPLAYSURF, WHITE, self.pos, (self.endpointupper[0], self.endpointupper[1]), 1)
            # pygame.draw.aaline(DISPLAYSURF, WHITE, self.pos, (self.endpointlower[0], self.endpointlower[1]), 1)

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

    def inWedge(self, entity):
        '''returns true if projectile or entity is detected. sets whether entity or projectile is detected.
        use triangle technique so we don't have to deal with unnormalized angles
        basically project the relative position vector onto the pov vectors and see if the projection is
        strictly positive in magnitude'''

        # compute necessary vectors:
        v0 = (self.endpointlower - self.pos)
        v1 = (self.endpointupper - self.pos)
        v2 = (entity.pos - self.pos)

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

        if u >= 0 and v >= 0 and self.owner != entity.owner:
            if entity.type == 'entity':
                self.detectEnemy = 1
            elif entity.type == 'projectile':
                self.detectProjectile = 1
                #print(self.owner + ' detects projectile!')
            return True
        else:
            self.detectEnemy = 0
            self.detectProjectile = 0
            return False

    def control(self, controlframe):
        ''' Based on the control frame input, the entity will be moved and/or rotated '''

        self.dir += controlframe.deltaHeading
        # normalize angle from -180 < angle <= 180
        self.dir = self.dir % 360
        self.dir = (self.dir + 360) % 360
        if self.dir > 180:
            self.dir -= 360
        delta = np.array((math.cos(math.radians(self.dir)), math.sin(math.radians(self.dir)))) * controlframe.forwardrelativemag
        delta2 = np.array((math.cos(math.radians(self.dir + 90)), math.sin(math.radians(self.dir + 90)))) * controlframe.sidewaysrelativemag

        #self.updatePos(controlframe.deltaDirection)
        self.updatePos(delta+delta2)
        self.prevdel = controlframe.deltaDirection




    def state(self):
        return self.hitwall, self.detectEnemy, self.detectProjectile, self.fired

    def reset(self):
        self.health = MAXHEALTH


class ControlFrame:
    def __init__(self, id):
        self.forwardrelativemag = 0
        self.sidewaysrelativemag = 0
        self.deltaHeading = 0
        self.deltaDirection = (0, 0)
        self.fire = False
        self.id = id
        self.pov = 10


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
        self.w1 = np.array(np.random.uniform(MINRANDPARM, MAXRANDPARM, (MAXNEURONSPERLAYER, 4)))
        self.b1 = np.array(np.random.uniform(MINRANDPARM, MAXRANDPARM, (MAXNEURONSPERLAYER,)))
        self.w2 = np.array(np.random.uniform(MINRANDPARM, MAXRANDPARM, (MAXNEURONSPERLAYER, MAXNEURONSPERLAYER)))
        self.b2 = np.array(np.random.uniform(MINRANDPARM, MAXRANDPARM, (MAXNEURONSPERLAYER,)))
        self.w3 = np.array(np.random.uniform(MINRANDPARM, MAXRANDPARM, (5, MAXNEURONSPERLAYER)))
        self.b3 = np.array(np.random.uniform(MINRANDPARM, MAXRANDPARM, (5,)))

        self.score = 0

        self.relativefitness = 0

        self.probability = 0

    def out(self, input):
        # output
        # -              -
        # |   delta X    |
        # |   delta Y    |
        # | delta Angle  |
        # | Fire boolean |
        # -              -

        layer1Out = np.tanh(self.w1 @ np.asarray(input) + self.b1)

        layer2Out = np.tanh(self.w2 @ np.asarray(layer1Out) + self.b2)

        preIndicator = (self.w3 @ layer2Out) + self.b3

        finalLayerOut = (np.tanh(preIndicator[0]),
                         np.tanh(preIndicator[1]),
                         np.tanh(preIndicator[2]),
                         np.piecewise(preIndicator[3], [preIndicator[3] < 0, preIndicator[3] >= 0], [0, 1]),
                         np.tanh(preIndicator[4]))

        #self.deltaDirection = (finalLayerOut[0], finalLayerOut[1])
        self.forwardrelativemag = finalLayerOut[0]
        self.sidewaysrelativemag = finalLayerOut[1]
        self.deltaHeading = finalLayerOut[2] * MAXSPINRATE
        self.fire = finalLayerOut[3]
        self.pov += finalLayerOut[4]
        if self.pov >= 50:
            self.pov = 50
        elif self.pov <= 1:
            self.pov = 1

        return self

    def updateWeights(self):
        pass


def getScore(NN):
    return NN.score

def getRelativeFitness(NN):
    return NN.relativefitness

def breed(NN1, NN2, owner):
    '''Takes in two NN's and outputs a child with randomly chosen Neuron weight clusters from both'''
    baby = NN(owner)

    for row in range(MAXNEURONSPERLAYER):
        choice = np.random.binomial(1, 0.5)
        if choice:
            baby.w1[row, :] = NN1.w1[row, :]
            # yes may get same weights for multiple neurons....
        else:
            baby.w1[row, :] = NN2.w1[row, :]

    for row in range(MAXNEURONSPERLAYER):
        choice = np.random.binomial(1, 0.5)
        if choice:
            baby.w2[row, :] = NN1.w2[row, :]
            # yes may get same weights for multiple neurons....
        else:
            baby.w2[row, :] = NN2.w2[row, :]

    for row in range(5):
        choice = np.random.binomial(1, 0.5)
        if choice:
            baby.w3[row, :] = NN1.w3[row, :]
            # yes may get same weights for multiple neurons....
        else:
            baby.w3[row, :] = NN2.w3[row, :]

    for weight in range(MAXNEURONSPERLAYER):
        choice = np.random.binomial(1, 0.5)
        if choice:
            baby.b1[weight] = NN1.b1[weight]
        else:
            baby.b1[weight] = NN2.b1[weight]

    for weight in range(MAXNEURONSPERLAYER):
        choice = np.random.binomial(1, 0.5)
        if choice:
            baby.b2[weight] = NN1.b2[weight]
        else:
            baby.b2[weight] = NN2.b2[weight]

    for weight in range(5):
        choice = np.random.binomial(1, 0.5)
        if choice:
            baby.b3[weight] = NN1.b3[weight]
        else:
            baby.b3[weight] = NN2.b3[weight]

    return baby


def mutate(NN):
    """currently mutates all weight clusters (rows) using normal distribution centered at the clusters"""
    choice = np.random.binomial(1, 0.1)
    if choice:
        multiplier = 100
        print('BIG MUTATION PROBABLE!')
    else:

        choice2 = np.random.binomial(1, 0.5)
        if choice2:
            multiplier = 1
        else:
            multiplier = 0.0001

    # weights
    for row in range(MAXNEURONSPERLAYER):
        NN.w1[row, :] = np.random.multivariate_normal(NN.w1[row, :], np.identity(len(NN.w1[row, :]))*multiplier)
        NN.w2[row, :] = np.random.multivariate_normal(NN.w2[row, :], np.identity(len(NN.w2[row, :]))*multiplier)
    for row in range(5):
        NN.w3[row, :] = np.random.multivariate_normal(NN.w3[row, :], np.identity(len(NN.w3[row, :]))*multiplier)
    # biases
    NN.b1 = np.random.multivariate_normal(NN.b1, np.identity(len(NN.b1))*multiplier)
    NN.b2 = np.random.multivariate_normal(NN.b2, np.identity(len(NN.b2))*multiplier)
    NN.b3 = np.random.multivariate_normal(NN.b3, np.identity(len(NN.b3))*multiplier)

    return NN


def setScore(NN):
    pass


def rouletteWheel(NNlist, n=1):
    totalfitness = 0
    offset = 0
    selected = []
    for i in range(len(NNlist)):
        totalfitness += NNlist[i].relativefitness

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
    # sort the list of nets
    sortlist = sorted(NNlist, key=getRelativeFitness, reverse=True)

    # pass on the top ciel(1/5*POPULATION) results
    m = len(NNlist)

    n = math.ceil(1/5*POPULATION)

    for i in range(int(n)):
        children.append(sortlist[i])
    print(str(n) + ' top results selected')

    # pass on children of top two fittest
    children.append(mutate(breed(sortlist[0], sortlist[1], NNlist[0].id)))
    children.append(mutate(breed(sortlist[0], sortlist[1], NNlist[0].id)))
    print('top two results bred twice')
    # pass on children of m - n - 2 roulette chosen pairs

    for net in range(int(m-n-2)):
        fittest = rouletteWheel(NNlist, 2)
        children.append(mutate(breed(fittest[0], fittest[1], NNlist[0].id)))
    print('total number of children: ' + str(len(children)))
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
    iteration += 1

    if iteration >= MAXITERATIONS or len(entities) < 2:

        for idx, net in enumerate(nets):
            print('Scoring ' + net.id + '...', end='')
            # score function
            try:
                net.score = (entities[idx].damagedealt * entities[idx].damagedealt / entities[idx].totaldamage) + entities[idx].health/MAXHEALTH
            except(ZeroDivisionError):
                # this means no damage!
                net.score = 0
            print(net.score)
        totalscore = 0
        for idx, net in enumerate(nets):
            totalscore += net.score
        for idx, net in enumerate(nets):
            try:
                net.relativefitness = net.score/totalscore
            except(ZeroDivisionError):
                net.relativefitness = 0


        iteration = 0

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

        print('Need to advance in Population')
        # reset bob and joe and and entities list
        print('respawning...', end='')
        joe = Entity((np.random.randint(1, MAXDISPX - 1), np.random.randint(1, MAXDISPY - 1)), 0, 15, CYAN,
                     DISPLAYSURF, 'joe')
        bob = Entity((np.random.randint(1, MAXDISPX - 1), np.random.randint(1, MAXDISPY - 1)), 0, 15, RED,
                     DISPLAYSURF, 'bob')
        entities = [bob, joe]
        print('done')
        print('generation: '+str(generation))
        print('POPULATION: ' + str(popindex + 1))
        nets = [NNlist1[popindex], NNlist2[popindex]]
        projectiles = []
        popindex += 1
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
            if event.key == K_1:
                keystate = 0
            if event.key == K_2:
                keystate = 1
            if event.key == K_3:
                keystate = 2
            if event.key == K_4:
                keystate = 3
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

    if entities:
        for idx, entity in enumerate(entities):
            entity.draw()
            entity.iniWedge(True)
            entity.inWedge(entities[0])
            entity.inWedge(entities[1])
            for projectile in projectiles:
                entity.inWedge(projectile)
            # create list of NNs for each entity
            nextmove = nets[idx].out(entity.state())
            entity.fired = False
            # print(str(nextmove.deltaDirection) + " " + str(nextmove.deltaHeading) + " " + str(nextmove.fire))
            entity.control(nextmove)
            entity.fov = nextmove.pov
            entity.projectileint += 1
            if nextmove.fire and entity.projectileint >= PROJECTILEINTERVAL:
                entity.projectileint = 0
                projectiles.append(
                    Entity((entity.pos[0], entity.pos[1]), entity.dir, 5, WHITE, DISPLAYSURF, entity.owner, 'projectile'))
                entity.totaldamage += 10
                entity.fired = True
    entities[:] = [x for x in entities if not x.health == 0]


    if runnormal:
        # draw all things here.
        if keystate == 0:
            displayupdateinterval = 5

        if keystate == 1:
            displayupdateinterval = 10

        if keystate == 2:
            displayupdateinterval = 25

        if keystate == 3:
            displayupdateinterval = 100


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

            #n 2pygame.draw.rect(DISPLAYSURF,WHITE,bigbox,5)
            pygame.draw.rect(DISPLAYSURF, WHITE, DISPLAYRECT, 2)
            pygame.display.update()
            DISPLAYSURF.fill(BLACK)
            DISPLAYSURF.blit(textSurf, textRect)
            tick = 0

