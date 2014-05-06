import math
import sys

class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
	
    def distance(self, p2):
        distance = math.sqrt((self.x-p2.x)**2 + (self.y-p2.y)**2)
        return distance
        
    def getDeltaXY(self, p2):
        dx = self.x - p2.x
        dy = self.y - p2.y
        return dx, dy
    
	#returns the closest point on the line segment formed by lineP1-lineP2 to the calling point
    def closestPointOnLine(self, line):
        lineP1 = line.p1
        lineP2 = line.p2
        
        lineLengthSquared = lineP1.distance(lineP2)
        if lineLengthSquared == 0.0:
            return self.distance(lineP1)
        
        tx = (self.x-lineP1.x)*(lineP2.x-lineP1.x)+(self.y-lineP1.y)*(lineP2.y-lineP1.y)
        tx = tx/((lineP2.x-lineP1.x)**2 + (lineP2.y-lineP1.y)**2)
        
        if tx < 0.0:
            return lineP1
        elif tx > 1.0:
            return lineP2
        else:
            pointOnLine = Point(lineP1.x + tx * (lineP2.x - lineP1.x), lineP1.y + tx * (lineP2.y - lineP1.y))
            return pointOnLine
            
    def distanceToLine(self, line):
        closestPoint = self.closestPointOnLine(line)
        return self.distance(closestPoint)
        
class Line(object):
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        
    def getSlope(self):
        if self.p1.x == self.p2.x:
            return None
        
        if self.p1.x < self.p2.x:
            return (self.p2.y-self.p1.y)/(self.p2.x-self.p1.x)
        else:
            return (self.p1.y-self.p2.y)/(self.p1.x-self.p2.x)
    
    #other is a Line object        
    def isPerpendicular(self, other):
        if self.getSlope() == None and other.getSlope() == 0.0:
            return True
            
        if self.getSlope() == 0.0 and other.getSlope() == None:
            return True		
		
        if other.getSlope() == None or other.getSlope() == 0.0:
            return False
        
        if self.getSlope() == ((1/other.getSlope())*-1):
            return True
        
        return False
    
    def getMidpoint(self):
        
        deltaX = 0.0
        deltaY = 0.0
        x = 0.0
        y = 0.0
        
        if self.p1.x != self.p2.x:
            deltaX = math.fabs(self.p2.x - self.p1.x)/2
            
        if self.p1.y != self.p2.y:
            deltaY = math.fabs(self.p2.y - self.p1.y)/2
            
        if self.p1.x < self.p2.x:
            x = self.p1.x + deltaX
        else:
            x = self.p2.x + deltaX
            
        if self.p1.y < self.p2.y:
            y = self.p1.y + deltaY
        else:
            y = self.p2.y + deltaY
        
        return Point(x, y)
