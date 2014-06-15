
import sys
import math
import random
import time

import Calculations as fields

from geo import Point, Line
from bzrc import BZRC, Command
from Kalman import Kalman
t = .5
class SuperUberAgent(object):
    
    def __init__(self, bzrc,tank,job):
        self.updatecounts = 0
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
               
        self.obstacles = []        
        #the .07125 comes from the 4 Ls world where 7.125% of the world was occupied
        self.time = time.time()
        self.locationList = []
        self.oldlocation = []
        
        self.startTime = time.time()
        

        self.mytanks = self.bzrc.get_mytanks()
        
    def angle(self,tank,target):
        angle = math.atan2((target.y-tank.y),(target.x-tank.x))
        return angle
    
    def getDeltaXY(self, tank, enemy):
        theta = self.angle(tank, enemy)
        distance = Point(tank.x, tank.y).distance(Point(enemy.x,enemy.y))
        
        deltaX = distance*math.cos(theta)
        deltaY = distance*math.sin(theta)
        
        return deltaX, deltaY
        
    def doKalman(self,X,Y):
        self.Kfilter = Kalman(X,Y)
        Mu,Sigma = self.Kfilter.runKalman(self.bzrc)
       
        enemyX = Mu.item((0,0))
        enemyY = Mu.item((3,0))
        
        distance = Point(self.tank.x, self.tank.y).distance(Point(enemyX,enemyY))
        
        if distance > 450:
            return
        
        pred = (distance/float(self.constants['shotspeed']))*(1.0/t)
        pred = int(pred+1)
        MuPred,garbage = self.Kfilter.predictiveKalman(Mu,Sigma,pred)
        targetX,targetY = MuPred.item((0,0)),MuPred.item((3,0))
        deltaX, deltaY = self.getDeltaXY(self.tank,Point(targetX,targetY))
        
        theta = math.atan2(deltaY,deltaX)
        theta = self.normalize_angle(theta-self.tank.angle)
        
        #distance = Point(tank.x, tank.y).distance(Point(targetX,targetY))
        
        if distance <= 390 and (theta < 0.2 and theta > -0.2):
            shoot = True
        else:
            shoot = False
        
        self.kalmanCommand(deltaX, deltaY, theta, shoot, self.tank)
    
    def update(self,tank):
        self.tank = tank
        
    def updateObstacles(self,grid):
        self.updatecounts += 1
        if(self.updatecounts > 100):
            return
        else:
            self.obstacles = grid
           
    
    def getFlagIndex(self):
        flags = self.bzrc.get_flags()
        i = 0
        for flag in flags:
            if flag.color == self.constants['team']:
                self.enemyFlag = (i + 1) % len(flags)  
                return i
            
            self.enemyFlag = i
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
        
        if (((time.time()) - self.startTime) > 100):
            self.job = "a"
        
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
            totalX=0
            totalY = 0
            for obstacle in self.obstacles:
                deltaX,deltaY = self.fields.getTangentialField2(self.tank,obstacle, 100, 10, "CW")
                totalX += deltaX
                totalY += deltaY
            if(self.tank.flag == "-"):
                delx,dely = self.fields.getTangentialField2(self.tank,self.flag, 100,2.5,"CCW")
                totalX += delx
                totalY += dely
                delx2,dely2 = self.fields.getAttractiveField(self.tank, flags[self.enemyFlag], 800, 2.5)
                totalX += delx2
                totalY += dely2
            else:
                delx,dely = self.fields.getAttractiveField(self.tank, self.base, 800, 40)
                totalX += delx
                totalY += dely
            # do offense
            self.sendCommand(totalX, totalY, self.tank)
        
        
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
        othertanks = self.bzrc.get_othertanks()
        me = Point(tank.x,tank.y)      
        
        cur = 100000
        mins = 100000
        enemy = Point(0,0)
        for other in othertanks:
            cur = Point(other.x,other.y).distance(me)
            if (cur < mins):
                mins = cur
                enemy = other
            
        if mins <= 200:
            self.doKalman(enemy.x, enemy.y)
            
        else:
     
            theta = math.atan2(totalY,totalX)
            theta = self.normalize_angle(theta-tank.angle)

            speed = math.sqrt(totalY**2+totalX**2)

            self.commands = []
            command = Command(tank.index,.15*speed,.85*theta,False)
            self.commands.append(command)
            self.bzrc.do_commands(self.commands)
            self.commands = []
        
    def kalmanCommand(self,totalX,totalY,theta,shoot,tank):
        p = Point(tank.x,tank.y)
        for obstacle in self.obstacles:
            if(p.distance(obstacle) < 50):
                deltaX,deltaY = self.fields.getTangentialField2(self.tank,obstacle, 100, 40,"CW")
                totalX = deltaX
                totalY = deltaY
                theta = math.atan2(totalY,totalX)
                theta = self.normalize_angle(theta-tank.angle)
    
        
                
        speed = math.sqrt(totalY**2+totalX**2)
        self.commands = []
        command = Command(tank.index,.15*speed,1.15*theta,True)
        self.commands.append(command)
        self.bzrc.do_commands(self.commands)
        self.commands = []

        


        
