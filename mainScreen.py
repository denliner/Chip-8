import numpy as np
from dataclasses import dataclass
import pygame
X=64
Y=32
BLACK=(0,0,0)
WHITE=(255,255,255)
RECTSIZE=8


@dataclass
class PIXEL:
    color : tuple
    position : pygame.Rect
    def __init__(self,x,y):
        self.color=BLACK
        self.position=pygame.Rect(x*RECTSIZE,
                y*RECTSIZE,RECTSIZE,RECTSIZE)

def initPixels(listPixel):
    for i,line in enumerate(listPixel):
        for j,pixel in enumerate(line):
            listPixel[i][j]=PIXEL(i,j)
            #if(i%(j+1)==0):
            #    listPixel[i][j].color=BLACK
            #else:
            #    listPixel[i][j].color=WHITE

def clearScreen(listPixel):
    for i,line in enumerate(listPixel):
        for j,pixel in enumerate(line):
            listPixel[i][j].color=BLACK

def updateScreen(listPixel,screen):
    for i,line in enumerate(listPixel):
        for j,pixel in enumerate(line):
            pix=listPixel[i][j]
            pygame.draw.rect(screen,pix.color, pix.position)



#print(pygame.Rect)
#np.empty((X,Y), dtype=pygame.Rect)
