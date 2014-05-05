import sys
import math
import time

from bzrc import BZRC, Command
from geo import Point, Line

class Obstacle(object):
    
    #corners is a list of 
    def __init__(self, in_corners):
        
        self.num_corners = 4
        self.corners = []
        
        for i in range(self.num_corners):
            x, y = in_corners[i]
            self.corners.append(Point(x, y))
            
        self.midpoint = self.getCenter()
        
        #print self.toString()
        
    def getCenter(self):
        coolLine = Line(self.corners[0], self.corners[2])
        midpoint = coolLine.getMidpoint()
        return midpoint
        
    def toString(self):
        rval = ""
        
        for i in range(self.num_corners):
            rval += str(self.corners[i].x)
            rval += ","
            rval += str(self.corners[i].y)
            rval += " "
            
        return rval
        
        
    
    
