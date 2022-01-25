import numpy as np
import pygame
import cpu
import mainScreen
import mainInput
import sys
X=64
Y=32
BLACK=(0,0,0)
WHITE=(255,255,255)
RECTSIZE=8
MS=1
CYCLE=4

def load_game(path,cpu8):
    with open(path, "rb") as f:
        game = f.read()
    for i,OP in enumerate(game):
        #print(i)
        cpu8.memory[i + cpu.START] = OP

def mainLoop():
    cpu8 = cpu.CPU()
    np.seterr(over='ignore')
    load_game(sys.argv[1],cpu8)
    listPixel=np.zeros((X,Y),dtype=mainScreen.PIXEL)
    mainScreen.initPixels(listPixel)
    (width, height) = (X*RECTSIZE, Y*RECTSIZE)
    background_colour = BLACK
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('chip-8')
    screen.fill(BLACK)
    #print("shape",np.shape(listPixel))
    pygame.display.flip()
    clock = pygame.time.Clock()
    running = True
    print(pygame.key)
    while(running):
        clock.tick(60)
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                case pygame.KEYDOWN:
                    if(event.scancode in mainInput.keys):
                        #print(event,pygame.K_q)
                        cpu8.keys[mainInput.keys[event.scancode]] = 1
                    elif(event.key == pygame.K_ESCAPE):
                        running = False
                case pygame.KEYUP:
                    if(event.scancode in mainInput.keys):
                        cpu8.keys[mainInput.keys[event.scancode]] = 0
        for c in range(0,CYCLE):
            cpu8.decodeInstruction(cpu8.getOpCode(),listPixel)
        mainScreen.updateScreen(listPixel,screen)
        pygame.display.update()
        cpu8.unCount()
        #pygame.time.delay(MS)


mainLoop()
