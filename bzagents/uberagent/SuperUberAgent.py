
import sys
import math
import random
import time

import Calculations as fields

from geo import Point, Line
from bzrc import BZRC, Command

class SuperUberAgent(object):
    
    def __init__(self, bzrc,tank,job):
        self.tank = tank
        self.bzrc = bzrc
        self.fields = fields.Calculations()
        self.throttle = .15
        self.commands = []
        self.constants = self.bzrc.get_constants()
        self.job = job
        self.base = bzrc.get_bases()[self.getFlagIndex()]
        c1 = Point(self.base.corner1_x,self.base.corner1_y)
        c3 = Point(self.base.corner3_x,self.base.corner3_y)
        line = Line(c1,c3)
        self.base = line.getMidpoint()
        flags = bzrc.get_flags()
        for flag in flags:
            if flag.color == self.constants['team']:
                self.flag = flag
               
                
        #the .07125 comes from the 4 Ls world where 7.125% of the world was occupied
        self.time = time.time()
        self.locationList = []
        self.oldlocation = []

        self.mytanks = self.bzrc.get_mytanks()
    
    def update(self,tank):
        self.tank = tank
        
    def updateGrid(self,grid):
        pass   
    
    def getFlagIndex(self):
        flags = self.bzrc.get_flags()
        i = 0
        for flag in flags:
            if flag.color == self.constants['team']:              
                return i
            i += 1
        return  
    
    def flagSafe(self,i):
        flags = self.bzrc.get_flags()
        if abs(flags[i].x - self.flag.x) > 10 or abs(flags[i].y-self.flag.y) > 10:
            self.flag = flags[i]
            return False
        else:
            self.flag = flags[i]
            return True
             
    
    def tick(self):
        
        if (self.job == "d"):
            i = self.getFlagIndex()
            
            if(self.flagSafe(i)):
                
                delx,dely = self.fields.getTangentialField2(self.tank,self.flag, 100,2.5,"CCW")
                delx2,dely2 = self.fields.getAttractiveField(self.tank, self.flag, 200, 2.5)
                delx2 = delx2*.2
                dely2 = dely2*.2
                delx = delx+delx2
                dely = dely + dely2
                
            else:
                delx,dely = self.fields.getAttractiveField(self.tank, self.flag, 800, 2.5)
            self.sendCommand(delx, dely, self.tank)
        if (self.job == "a"):
            flags = self.bzrc.get_flags()
            
            if(self.tank.flag == "-"):
                delx,dely = self.fields.getAttractiveField(self.tank, flags[1], 800, 2.5)
            else:
                delx,dely = self.fields.getAttractiveField(self.tank, self.base, 800, 40)
            # do offense
            self.sendCommand(delx, dely, self.tank)
        
        
    def goToPoint(self,tank,target):
        totalX = 0
        totalY = 0

        deltaX,deltaY = self.fields.getAttractiveField(tank, target, 800, 5)
   
        totalX += deltaX
        totalY += deltaY
        
        totalX += random.randrange(-300,300)
        totalY += random.randrange(-300,300)
        
        self.sendCommand(totalY, totalX, tank)
        
    def normalize_angle(self, angle):
        """Make any angle be between +/- pi."""
        angle -= 2 * math.pi * int (angle / (2 * math.pi))
        if angle <= -math.pi:
            angle += 2 * math.pi
        elif angle > math.pi:
            angle -= 2 * math.pi
        return angle
        
    def sendCommand(self,totalX,totalY,tank):
        shoot = True
     
        theta = math.atan2(totalY,totalX)
        theta = self.normalize_angle(theta-tank.angle)

        speed = math.sqrt(totalY**2+totalX**2)

        self.commands = []
        command = Command(tank.index,speed,.35*theta,shoot)
        self.commands.append(command)
        self.bzrc.do_commands(self.commands)
        self.commands = []
        

        


        
