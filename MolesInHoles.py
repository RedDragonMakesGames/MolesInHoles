import pygame
from pygame.locals import *
import random
import math
import sys

#Defines
XHOLES = 5
YHOLES = 5
XSPACING = 20
YSPACING = 20
TOPBAR = 100
MOLERATE = 5
MAXMOLES = 10
MOLECHANCE = 5
MOLELIFETIME = 60
NOSETHRESHOLD = 10  #The number of frames where just the nose will show at the start and end
TIMELIMIT = 10

#Ofsets to make sure the hammer shows where the cursor is
HAMMEROFFX = -10
HAMMEROFFY = -20

#Helper functions
def CheckTounching(pos1, pos2, size):
    if ((pos1[0] >= pos2[0] and pos1[0] <= pos2[0] + size[0]) and (pos1[1] >= pos2[1] and pos1[1] <= pos2[1] + size[1])):
        return True
    else:
        return False

class Mole:
    def __init__(self, xpos, ypos):
        self.pos = (xpos, ypos)
        self.timeToLive = MOLELIFETIME
        self.isNose = True

    def Tick(self):
        self.timeToLive -= 1
        if (self.timeToLive < NOSETHRESHOLD or self.timeToLive > (MOLELIFETIME - NOSETHRESHOLD)):
            self.isNose = True
        else:
            self.isNose = False

class MolesInHoles:
    def __init__(self, setUp):
        self.xHoles = setUp[0]
        self.yHoles = setUp[1]
        self.rate = setUp[2]
        self.time = setUp[3]
        pygame.init()
        pygame.display.set_caption("Moles in holes")
        #Hide cursor
        pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))

        self.clock = pygame.time.Clock()

        #Load assets. Do this before setting the screen size so we can base the screen size on the size of the holes
        self.hole = pygame.image.load('Assets/hole.png')
        self.mole = pygame.image.load('Assets/mole.png')
        self.nose = pygame.image.load('Assets/nose.png')
        self.hammer = pygame.image.load('Assets/hammer.png')
        self.hammerDown = pygame.image.load('Assets/hammer_down.png')
        self.retry = pygame.image.load('Assets/retry.png')

        self.screen = pygame.display.set_mode((self.hole.get_size()[0]* (self.xHoles) + XSPACING * (self.xHoles + 1), self.hole.get_size()[1] * (self.yHoles) + YSPACING * (self.yHoles + 1) + TOPBAR))

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((200,200,200))

        if pygame.font:
            self.font = pygame.font.Font(None, 40)

        self.score = 0
        self.spawnTick = 0
        self.hammerPos = (0,0)
        self.hammerIsDown = False
        self.timeOver = False

        self.moles = []

        #Start the main gameplay loop
        #self.Run()

    def Run(self):
        self.finished = False

        while not self.finished:
            #Handle input
            self.HandleInput()

            #Tick moles, and remove any that have expired
            for m in self.moles:
                m.Tick()
                if m.timeToLive <= 0:
                    self.moles.remove(m)

            if not self.timeOver:
                self.SpawnMoles()

            #Draw screen
            self.Draw()

            self.clock.tick(60)
        
        pygame.quit()
        return True

    def HandleInput(self):
        pos = pygame.mouse.get_pos()
        self.hammerPos = (pos[0] + HAMMEROFFX, pos[1] + HAMMEROFFY)
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                self.hammerIsDown = True
                hitMole = False
                for m in self.moles:
                    if CheckTounching(pos, self.GameCoordToScreenPos(m.pos), self.mole.get_size()):
                        #You've clicked on a mole, whack it and increase score
                        self.score += 1
                        self.moles.remove(m)
                        hitMole = True
                if hitMole == False and self.timeOver == False:
                    #You missed, so reduce score
                    self.score -= 1
                if self.timeOver == True:
                    if CheckTounching(pos, (self.screen.get_size()[0] - self.retry.get_size()[0] - XSPACING, 3 * YSPACING), self.retry.get_size()):
                        self.finished = True
            
            elif event.type == MOUSEBUTTONUP:
                self.hammerIsDown = False
    
    def Draw(self):
        #clear screen
        self.screen.blit(self.background, (0,0))

        #Draw holes
        for x in range(0, self.xHoles):
            for y in range(0, self.yHoles):
                self.screen.blit(self.hole, (self.GameCoordToScreenX(x), self.GameCoordToScreenY(y)))

        #Draw moles
        for m in self.moles:
            if m.isNose == True:
                img = self.nose
            else:
                img = self.mole
            self.screen.blit(img, (self.GameCoordToScreenX(m.pos[0]), self.GameCoordToScreenY(m.pos[1])))
        
        #Draw hammer cursor
        if self.hammerIsDown:
            self.screen.blit(self.hammerDown, self.hammerPos)
        else:
            self.screen.blit(self.hammer, self.hammerPos)

        #Draw score
        scoreStr = "Score: " + str(self.score)
        scoreTxt = self.font.render(scoreStr, True, (10,10,10))
        self.screen.blit(scoreTxt, (XSPACING,YSPACING))

        #Draw timer
        timeElapsed = pygame.time.get_ticks()/1000
        timeRemaining = math.floor(self.time - timeElapsed)
        if timeRemaining <= 0:
            self.timeOver = True
            timeRemaining = 0
        timeStr = "Time remaining: " + str(timeRemaining)
        timeTxt = self.font.render(timeStr, True, (10,10,10))
        self.screen.blit(timeTxt, (XSPACING, 3 * YSPACING))

        if self.timeOver == True:
            endStr = "Time over!"
            endText = self.font.render(endStr, True, (10,10,10))
            self.screen.blit(endText, (self.screen.get_size()[0] - endText.get_size()[0] - XSPACING, YSPACING))
            #Draw restart icon
            self.screen.blit(self.retry, (self.screen.get_size()[0] - self.retry.get_size()[0] - XSPACING, 3 * YSPACING))

        #Refresh the screen
        pygame.display.flip()

    def SpawnMoles(self):
        #Wait until the spawn rate
        self.spawnTick += 1
        if self.spawnTick < self.rate:
            return
        else:
            self.spawnTick = 0
        
        #If we've already got all our moles, don't spawn any more
        if len(self.moles) >= MAXMOLES:
            return

        #Only spawn a mole if we hit the chance
        if random.randint(0, MOLECHANCE) != 0:
            return
        
        #We're good to spawn a mole, find a new spot
        valid = False
        x = 0
        y = 0
        while (valid == False):
            valid = True
            x = random.randint(0, self.xHoles - 1)
            y = random.randint(0, self.yHoles - 1)
            pos = (x, y)
            for m in self.moles:
                if m.pos == pos:
                    valid = False
        
        #We've found our spot, spawn the mole
        self.moles.append(Mole(x,y))

    def GameCoordToScreenX(self, x):
        return (x * self.hole.get_size()[0] + (x + 1) * XSPACING)

    def GameCoordToScreenY(self, y):
        return (y * self.hole.get_size()[1] + (y + 1) * YSPACING + TOPBAR)

    def GameCoordToScreenPos(self, pos):
        return (self.GameCoordToScreenX(pos[0]), self.GameCoordToScreenY(pos[1]))

#game = MolesInHoles()