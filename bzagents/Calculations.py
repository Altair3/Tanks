import math
    
class Calculations(object):
    def __init__ (self):
        self.Kp = .1
        self.Kd = .2
     
    ''' The PD controller calculations'''
    def calculateAlpha(self,current,target,oldError,elapsedTime,tank):
        '''tank has x,y,angle,etc. use bzrc to see the tank'''
        # y(t) - x(t) is error
        error = (target) - (current)
        alpha = self.Kp*error
    
        return alpha # return alpha here when it works
    
    def distance(self, tank,target):
        distance = math.sqrt((target.x-tank.x)**2 + (target.y-tank.y)**2)
        return distance
    
    def angle(self,tank,target):
        angle = math.atan2((target.y-tank.y),(target.x-tank.x))
        return angle
    
    """ returns the change in x and y for an attractive field, """
    def getAttractiveField(self,tank,target,spread,radius):
        alpha = 1       
        deltax = 0
        deltay = 0
        d = self.distance(tank, target)
        theta = self.angle(tank, target)
        
        if d < radius:           
            return deltax,deltay
        elif radius <= d and d <= (spread + radius):
            deltax = alpha * (d-radius)*math.cos(theta)
            deltay = alpha * (d-radius)*math.sin(theta)
            return deltax,deltay
        elif d > (spread + radius):
            deltax = alpha * spread * math.cos(theta)
            deltay = alpha * spread * math.sin(theta)
            return deltax,deltay
        
    """ returns the change in x and y for a repulsive field """
    def getRepulsiveField(self,tank,target,spread,radius):
        alpha = 1
        deltax = 0
        deltay = 0
        d = self.distance(tank, target)
        theta = self.angle(tank, target)
        
        if d < radius:    
            signx = math.copysign(1.0,math.cos(theta))
            signy = math.copysign(1.0, math.sin(theta))
            ''' inthe math online it says to use infinity, not sure what we want to do here'''
            deltax = -1 * signx * 10000000   
            deltay = -1 * signy * 10000000
            return deltax,deltay
        
        elif radius <= d and d <= (spread + radius):
            
            deltax = -1 * alpha * (spread+radius-d)*math.cos(theta)
            deltay = -1 * alpha * (spread+radius-d)*math.sin(theta)
            return deltax,deltay
        
        elif d > (spread + radius):                
            return deltax,deltay    

    def getTangentialObstacleField(self, tank, target, oldTank, elapsedTime):
        
        deltaX = 0.0
        deltaY = 0.0
        
        tankPosition = Point(tank.x, tank.y)
        closestPoint = tankPosition.closestPointOnLine(target.p1, target.p2)
        
        if self.distance(tankPosition, closestPoint) < target.spread:
            lineToTarget = Line(tankPosition, closestPoint)
            if target.isPerpendicular(lineToTarget):
                midpoint = target.getMidpoint()
                if closestPoint.x < midpoint.x:
                    deltaX = -1.0
                elif closestPoint.x > midpoint.x:
                    deltaX = 1.0
                else:
                    deltaX = 0.0
                    
                if closestPoint.y < midpoint.y:
                    if target.getSlope() == 0.0:
                        deltaY = 0.0
                    elif target.getSlope() == None:
                        deltaY = -1.0
                    else:
                        deltaY = -1.0 * target.getSlope()
                elif closestPoint.y > midpoint.y:
                    if target.getSlope() == 0:
                        deltaY = 0.0
                    elif target.getSlope() == None:
                        deltaY = 1.0
                    else:
                        deltaY = 1.0 * target.getSlope()
                else:
                    deltaY = 0.0
                    
                
                
                    
        return deltaX, deltaY  
    
    
    def getTangentialField2(self,tank,target,spread,radius,direction):
        alpha = .25
        deltax = 0
        deltay = 0
        d = self.distance(tank, target)
        theta = self.angle(tank, target)
        if direction == "CW":
            theta  = theta - math.pi/2
        elif direction == "CCW":
            theta = theta + math.pi/2
            
        if d < radius:    
            signx = math.copysign(1.0,math.cos(theta))
            signy = math.copysign(1.0, math.sin(theta))
            ''' inthe math online it says to use infinity, not sure what we want to do here'''
            deltax = -1 * signx * 10000000      
            deltay = -1 * signy * 10000000   
            return deltax,deltay
        
        elif radius <= d and d <= (spread + radius):
            
            deltax = -1 * alpha * (spread+radius-d)*math.cos(theta)
            deltay = -1 * alpha * (spread+radius-d)*math.sin(theta)
            return deltax,deltay
        
        elif d > (spread + radius):                
            return deltax,deltay
