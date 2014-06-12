import sys
import math
import random
import time
import Calculations as fields

from geo import Point

from bzrc import BZRC, Command


class BayesAgent(object):
    
    def __init__(self, bzrc,tank,grid):
        self.tank = tank
        self.bzrc = bzrc
        self.fields = fields.Calculations()
        self.throttle = .15
        self.commands = []
        self.constants = self.bzrc.get_constants()
        self.truePositive = float(self.constants['truepositive'])
        self.falseNegative = 1.0 - float(self.truePositive)
        self.trueNegative = float(self.constants['truenegative'])
        self.falsePositive = 1.0 - self.trueNegative
        self.grid = grid
        
        self.time = time.time()
        self.locationList = []
        self.oldlocation = []
        
       
        for i in range(10):
            self.locationList.append(self.getRandomCoordinate(i))
            self.oldlocation.append(Point(self.tank.x, self.tank.y))
            
    def update(self,tank):
        self.tank = tank
    
    def tick(self):
        self.commands = []
        curtime = time.time()
        
               
        curLocation = Point(self.tank.x, self.tank.y)
        target = self.locationList[self.tank.index]
        
        if curLocation.distance(target) < 10:
            target = self.getRandomCoordinate(self.tank.index)
            
            while self.grid.get(target.x, target.y) > .95:
                target = self.getRandomCoordinate(self.tank.index)
            
            self.locationList[self.tank.index] = target
            
        self.oldlocation[self.tank.index] = curLocation
        self.goToPoint(self.tank, target)
            
        if(curtime - self.time > 4.25 ):

            command = Command(self.tank.index,0,0,False)
            self.commands = []
            self.commands.append(command)
            self.bzrc.do_commands(self.commands)
            self.commands = []
            self.getObservation(self.tank)
            self.time = time.time()
        
        
    def getObservation(self, tank):
        if tank.status != 'alive':
            return
        pos, size, grid = self.bzrc.get_occgrid(tank.index)
        self.updateGrid(pos, size, grid)
        

        
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
        
    def sendCommand(self,totalY,totalX,tank):
        shoot = False
     
        theta = math.atan2(totalY,totalX)
        theta = self.normalize_angle(theta-tank.angle)

        speed = self.throttle*math.sqrt(totalY**2+totalX**2)

        self.commands = []
        command = Command(tank.index,speed,.35*theta,shoot)
        self.commands.append(command)
        self.bzrc.do_commands(self.commands)
        self.commands = []
        
    def getRandomCoordinate(self, tankIndex):
        #1 and 2: quadrant 1 (x,y)
        if tankIndex == 1 or tankIndex == 2:
            rval = Point(random.randrange(0,400), random.randrange(0,400))
        #3 and 4: quadrant 2 (x,-y)
        elif tankIndex == 3 or tankIndex == 4:
            rval = Point(random.randrange(0,400), random.randrange(-400,0))
        #5 and 6: quadrant 3 (-x,-y)
        elif tankIndex == 5 or tankIndex == 6:
            rval = Point(random.randrange(-400,0), random.randrange(-400,0))
        #7 and 8: quadrant 4 (-x, y)
        elif tankIndex == 7 or tankIndex == 8:
            rval = Point(random.randrange(-400,0), random.randrange(0,400))
        #9 and 10: middle ([-200,200],[-200,200])
        else:
            rval = Point(random.randrange(-200,200), random.randrange(-200,200))
        return rval
        
    '''
    observation: the object returned by bzrc
    '''
    def updateGrid(self, obsPos, obsSize, obsGrid):
        xPos, yPos = obsPos
              
        curX = xPos
        curY = yPos
        
        for i in obsGrid:
            for j in i:
                
                curValue = self.grid.get(curX, curY)
                obsValue = j

               
                if obsValue == 1:
                    newP = self.truePositive*curValue/(self.truePositive*curValue+self.falsePositive*(1-curValue))
                
                else:
                    newP = self.falsePositive*curValue/(self.falsePositive*curValue+self.trueNegative*(1-curValue))
                   
                
                self.grid.set(curX,curY, newP)
                
                curY += 1
            curX += 1
            curY = yPos
        
