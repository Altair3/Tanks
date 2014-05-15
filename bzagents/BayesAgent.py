import sys
import math
import random
import time
import numpy as np
import Visualizer as vs
import Calculations as fields
from geo import Point, Line
from bzrc import BZRC, Command

class BayesAgent(object):
    
    def __init__(self, bzrc):
        
        self.bzrc = bzrc
        self.fields = fields.Calculations()
        self.throttle = .15
        self.commands = []
        self.constants = self.bzrc.get_constants()
        self.truePositive = float(self.constants['truepositive'])
        self.falseNegative = 1.0 - float(self.truePositive)
        self.trueNegative = float(self.constants['truenegative'])
        self.falsePositive = 1.0 - self.trueNegative
        self.grid = OccGrid(800, 800, .07125)
        #the .07125 comes from the 4 Ls world where 7.125% of the world was occupied
        
        vs.init_window(800,800)
        self.grid.draw()
		
    def tick(self, prev_time):
        
        self.commands = []
        self.mytanks = self.bzrc.get_mytanks()
        for tank in self.mytanks:
            target = Point(0.0, 0.0)
            self.goToPoint(tank, target)
            
            self.getObservation(tank)
        
    def getObservation(self, tank):
        pos, size, grid = self.bzrc.get_occgrid(tank.index)
        self.updateGrid(pos, size, grid)
        self.grid.draw()
        
    def goToPoint(self,tank,target):
        totalX = 0
        totalY = 0

        deltaX,deltaY = self.fields.getAttractiveField(tank, target, 800, 5)
      
   
        totalX += deltaX
        totalY += deltaY
        
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

        command = Command(tank.index,self.throttle*math.sqrt(totalY**2+totalX**2),.85*theta,shoot)
        self.commands.append(command)
        self.bzrc.do_commands(self.commands)
      
        
    '''
    observation: the object returned by bzrc
    '''
    def updateGrid(self, obsPos, obsSize, obsGrid):
        xPos, yPos = obsPos
        xSize, ySize = obsSize
        
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
        

'''
Created by Chris

Creates a grid like structure that goes from [-x,x] and [-y,y]
'''
class OccGrid(object):
    
    '''
    sizeX: the total length of the X part of the grid
    sizeY: the total length of the Y part of the grid
    prior: the initial prior value of each cell (what are the beginning chances that each cell is occupied?)
    '''
    def __init__(self, sizeX, sizeY, prior):
        self.sizeX = sizeX + 1 #+1 for zero
        self.sizeY = sizeY + 1
        self.xMax = int(self.sizeX/2)
        self.yMax = int(self.sizeY/2)
        
        self.prior = prior
        
        self.grid = np.zeros([self.sizeX, self.sizeY])
        self.grid.fill(prior)
        
    def convert(self, x, y):
        return (self.yMax-y), (x+self.xMax)
    '''
    calls the update in the OpenGl lib
    '''
    def draw(self):
		vs.update_grid(self.grid)
		vs.draw_grid()
		  
    '''
    x: the x coordinate
    y: the y coordinate
    return: the value at [x,y]
    '''
    def get(self, x, y):
        xIndex, yIndex = self.convert(x, y)
        return self.grid[xIndex, yIndex]
    
    '''
    x: the x coordinate
    y: the y coordinate
    value: the value to be set in that coordinate
    '''    
    def set(self, x, y, value):
        xIndex, yIndex = self.convert(x, y)
        self.grid[xIndex, yIndex] = value
        
    '''
    creates a string representation of the grid
    '''
    def toString(self):
        rval = ""
        for x in self.grid:
            for y in x:
                rval += "[" + str(y) + "]"
            rval += "\n"
        
        return rval

def main():
    
    # Process CLI arguments.
    try:
        execname, host, port  = sys.argv
    except ValueError:
        execname = sys.argv[0]
        print >>sys.stderr, '%s: incorrect number of arguments' % execname
        print >>sys.stderr, 'usage: %s hostname port' % sys.argv[0]
        sys.exit(-1)

    # Connect.
    bzrc = BZRC(host, int(port))
    agent = BayesAgent(bzrc)
    
    prev_time = time.time()

    # Run the agent
    try:
        while True:
            agent.tick(prev_time)
            
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()
    
    '''
    #Grid test stuff
    grid = OccGrid(10,10,0)
    
    grid.set(0,5, 1)
    
    print grid.toString()
    '''


if __name__ == '__main__':
    main()
        
