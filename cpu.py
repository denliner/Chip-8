import numpy as np
from collections import deque 
from dataclasses import dataclass
import random
import pygame
import mainScreen
import mainInput

MEMSIZE=4096
START = 0x200
@dataclass
class CPU:
    memory: np.ndarray
    RegisterV: np.ndarray
    RegisterI: np.uint16
    jump: np.ndarray
    nbJump: np.uint8
    systime: np.uint8
    soundtime: np.uint8
    programCounter: np.uint16
    keys:  np.ndarray
  
    def __init__(self):
        self.memory=np.zeros(MEMSIZE,dtype=np.uint8)
        self.RegisterV=np.zeros(16,dtype=np.uint8)
        self.RegisterI=np.uint16(0)
        self.jump=np.zeros(16,dtype=np.uint16)
        self.nbJump=np.uint8(0)
        self.systime=np.uint8(0)
        self.soundtime=np.uint8(0)
        self.programCounter=np.uint16(START)
        self.keys = np.zeros( 16,dtype = np.uint8 )

        for i,font in enumerate(mainInput.fonts):
            self.memory[i] = font

    def unCount(self):
        if self.systime>0:
            self.systime=self.systime-1
        if self.soundtime>0:
            self.soundtime=self.soundtime-1

    def getOpCode(self):
        return ((self.memory[self.programCounter]<<8) 
                + self.memory[self.programCounter+1])

    def eights(self,OPcode,second,third,fourth):
        match fourth:
            case 0x0:
                self.RegisterV[second] = self.RegisterV[third]
            case 0x1:
                self.RegisterV[second] = ( self.RegisterV[third] | self.RegisterV[second] )
            case 0x2: #8XY2 
                self.RegisterV[second] = ( self.RegisterV[third] &  self.RegisterV[second] )
            case 0x3:
                self.RegisterV[second] = ( self.RegisterV[third] ^ self.RegisterV[second] )
            case 0x4:
                summ= ( self.RegisterV[second] +  self.RegisterV[third] )
                if(( int(self.RegisterV[second]) +  int(self.RegisterV[third] )) >0xFF):
                    self.RegisterV[0xF] = 1
                else:
                    self.RegisterV[0xF] = 0
                self.RegisterV[second] = summ
            case 0x5:
                summ= ( self.RegisterV[second] -  self.RegisterV[third] )
                if(self.RegisterV[second]<self.RegisterV[third] ):
                    self.RegisterV[0xF] = 0
                else:
                    self.RegisterV[0xF] = 1
                self.RegisterV[second] = summ
            case 0x6:
                self.RegisterV[0xF] = self.RegisterV[second] & 0x01
                self.RegisterV[second] = (self.RegisterV[second] >> 1) %256
            case 0x7:
                summ= ( self.RegisterV[third] -  self.RegisterV[second] )
                if(self.RegisterV[second]>self.RegisterV[third]):
                    self.RegisterV[0xF] = 0
                else:
                    self.RegisterV[0xF] = 1
                self.RegisterV[second] = summ
            case 0xE:
                self.RegisterV[0xF] = self.RegisterV[second] >> 7 & 0x01
                self.RegisterV[second] = (self.RegisterV[second] << 1) %256


    def zeroes(self,OPcode,listPixel):
        if(OPcode == 0x00E0):
            mainScreen.clearScreen(listPixel)
        elif(OPcode == 0x00EE):
            if(self.nbJump>0):
                self.nbJump-=1
                self.programCounter  = self.jump[self.nbJump]

    def jumpTo(self,NNN):
        self.programCounter = NNN
        self.programCounter-=2

    def exec(self,NNN):
        self.jump[self.nbJump]=self.programCounter
        self.nbJump = self.nbJump + 1 if self.nbJump<15 else self.nbJump
        self.programCounter = NNN
        self.programCounter-=2

    def skip(self,NotEQ,x,y):
        if(NotEQ):
            if(not x==y):
                self.programCounter+=2
        else:
            if( x==y ):
                self.programCounter+=2

    def define(self,x,y):
        if(x is not None):
            self.RegisterV[x] = y
        else:
            self.RegisterI = y
    
    def add(self,second,NN):
        if(second is not None):
            self.RegisterV[second]= (self.RegisterV[second] + NN) %256
        else:
            summ = (self.RegisterI + NN)
            #self.RegisterI = summ%256
            if(summ>0xFFF):
                self.RegisterV[0xF] = 1
            else:
                self.RegisterV[0xF] = 0
            self.RegisterI = summ

    def randomDef(self,NN,second):
        self.RegisterV[second]= random.randint(0,NN-1)

    def drawSprite(self,second,third,fourth,listPixel):
        self.RegisterV[0xF] = 0
        for i in range(0,fourth):
            pix = self.memory[self.RegisterI+i]
            y = (self.RegisterV[third]+i)%mainScreen.Y
            for j in range(0,8):
                index = 7-j
                x = (self.RegisterV[second]+j)%mainScreen.X
                if(not (((pix) & (0x1<<index)) == 0 ) ):
                    if(listPixel[x][y].color  == mainScreen.WHITE):
                        listPixel[x][y].color = mainScreen.BLACK
                        self.RegisterV[0xF] = 1
                    else:
                        listPixel[x][y].color = mainScreen.WHITE

    def skipE(self,second,NN):
        if(NN == 0xA1):
            if(self.keys[self.RegisterV[second]] == 0 ):
                self.programCounter+=2
        elif(NN == 0x9E):
            if(self.keys[self.RegisterV[second]] == 1 ):
                self.programCounter+=2
        
    def waitKeyPress(self):
        condition = True
        while(condition):
            event = pygame.event.wait()
            match event.type:
                case pygame.QUIT:
                    condition = False
                case pygame.KEYDOWN:
                    if(event.scancode in mainInput.keys):
                        self.keys[mainInput.keys[event.scancode]] = 1
                        condition = False
        self.programCounter+=2

    def defineTime(self,isSound,val):
        if(isSound):
            self.soundtime = val
        else:
            self.systime = val
        

    def F_instructions(self,OPcode,first,second,third,fourth,NN,NNN):
        match NN:
            case 0x07:
                self.define(second,self.systime)
            case 0x0A:
                self.waitKeyPress()
            case 0x15:
                self.defineTime(False,second)
            case 0x18:
                self.defineTime(True,second)
            case 0x1E:
                #print("1 E\n\n")
                self.add(None,self.RegisterV[second])
            case 0x29:
                self.RegisterI = self.RegisterV[second] * 5
            case 0x33:
                store = "{0:0=3d}".format(self.RegisterV[second])
                for ind in range(0,3):
                    self.memory[self.RegisterI + ind] = int(store[ind])
            case 0x55:
                for index in range(0,second+1):
                    self.memory[self.RegisterI + index] = self.RegisterV[index]

            case 0x65:
                for index in range(0,second+1):
                    self.RegisterV[index] = self.memory[self.RegisterI + index]


    
    def decodeInstruction(self,OPcode,listPixel):
        #print(hex(OPcode))
        first  = (OPcode & 0xF000) >> 12
        second = (OPcode & 0x0F00) >> 8
        third  = (OPcode & 0x00F0) >> 4
        fourth = (OPcode & 0x000F)
        NN     = (OPcode & 0x00FF)
        NNN    = (OPcode & 0x0FFF)
        match first:
            case 0x0:
                self.zeroes(OPcode,listPixel)
            case 0x1:
                self.jumpTo(NNN)
            case 0x2:
                self.exec(NNN)
            case 0x3:
                self.skip(0,self.RegisterV[second],NN)
            case 0x4:
                self.skip(1,self.RegisterV[second],NN)
            case 0x5:
                self.skip(0,self.RegisterV[second],self.RegisterV[third])
            case 0x6:
                self.define(second,NN)
            case 0x7:
                self.add(second,NN)
            case 0x8:
                self.eights(OPcode,second,third,fourth)
            case 0x9:
                self.skip(1,self.RegisterV[second],self.RegisterV[third])
            case 0xA:
                self.define(None,NNN)
            case 0xB:
                self.jumpTo(NNN+self.RegisterV[0])
            case 0xC:
                self.randomDef(NN,second)
            case 0xD:
                self.drawSprite(second,third,fourth,listPixel)
            case 0xE:
                self.skipE(second,NN)
            case 0xF:
                self.F_instructions(OPcode,first,second,
                        third,fourth,NN,NNN)
    
        self.programCounter+=2
        #print(self.programCounter)
    




