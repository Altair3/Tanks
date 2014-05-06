'''
Created on May 1, 2014

@author: dml66
'''

import sys
import math
import time

from bzrc import BZRC, Command
from obstacle import Obstacle
from geo import Point, Line

class PFAgent(object):
    
    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        self.throttle = .15
        self.obstacles = []
        self.fields = Calculations()
        self.flagIndex = self.getIndex()
        self.base = bzrc.get_bases()[self.flagIndex]
        
        c1 = Point(self.base.corner1_x, self.base.corner1_y)
        c3 = Point(self.base.corner3_x, self.base.corner3_y)
        line = Line(c1, c3)
        self.base = line.getMidpoint()
        
        
        for obs in bzrc.get_obstacles():
            self.obstacles.append(Obstacle(obs))
    
    def getIndex(self):
        flags = self.bzrc.get_flags()
        i = 0
        for flag in flags:
            if flag.color == self.constants['team']:              
                return i
            i += 1
        return    
    def captureFlag(self,tank,flags,flagIndex,time_diff):
       
            totalX = 0
            totalY = 0
            '''could add code here  Need to go and get the flag, and if you have it come back. also avoid enemies and obstacles etc.'''
   
            deltaX,deltaY = self.fields.getAttractiveField(tank, flags[flagIndex], 800, 5)
          
            totalX += deltaX
            totalY += deltaY
      
            for obstacle in self.obstacles:
               
                deltaX,deltaY = self.fields.getRepulsiveField(tank,obstacle.midpoint, obstacle.distanceToCenter*1.2, obstacle.distanceToCenter)
                #deltaX,deltaY = self.fields.getTangentialField2(tank,obstacle.midpoint, obstacle.distanceToCenter, obstacle.distanceToCenter, "CCW")
                totalX += deltaX
                totalY += deltaY
                
            
            '''can also calculate a repulsion for enemies'''
            for enemy in self.enemies:             
                deltaX,deltaY = self.fields.getTangentialField2(tank, enemy, 20, 1, "CW")
                totalX += deltaX
                totalY += deltaY
                pass
            '''this is calculating the angle between where you currently are and where you are trying to be updates accordingly'''
            ''' The throttle decreases speed as you approach the object of interest, in theory
                totalX and Y are where you want to be'''
            theta = math.atan2(totalY, totalX)
            theta = theta - tank.angle
            #theta = self.fields.calculateAlpha(tank.angle, theta, 0, time_diff,tank)
            #accel = self.fields.calculateAlpha(current, target, 0, time_diff, tank)
            command = Command(tank.index,self.throttle*math.sqrt(totalY**2+totalX**2),theta,False)
            self.commands.append(command)
     
            
            '''should we log these results?'''
            self.bzrc.do_commands(self.commands)
    
   
    def returnFlag(self,tank,flags,time_diff):
            totalX = 0
            totalY = 0
            '''could add code here  Need to go and get the flag, and if you have it come back. also avoid enemies and obstacles etc.'''
   
            deltaX,deltaY = self.fields.getAttractiveField(tank,self.base,800,5)
          
            totalX += deltaX
            totalY += deltaY
      
            for obstacle in self.obstacles:
               
                deltaX,deltaY = self.fields.getRepulsiveField(tank,obstacle.midpoint, obstacle.distanceToCenter*1.2, obstacle.distanceToCenter)
                #deltaX,deltaY = self.fields.getTangentialField2(tank,obstacle.midpoint, obstacle.distanceToCenter, obstacle.distanceToCenter, "CCW")
                totalX += deltaX
                totalY += deltaY
              
            
            '''can also calculate a repulsion for enemies'''
            for enemy in self.enemies:             
                deltaX,deltaY = self.fields.getTangentialField2(tank, enemy, 25, 2, "CCW")
                totalX += deltaX
                totalY += deltaY
           
            '''this is calculating the angle between where you currently are and where you are trying to be updates accordingly'''
            ''' The throttle decreases speed as you approach the object of interest, in theory
                totalX and Y are where you want to be'''
            theta = math.atan2(totalY, totalX)
            theta = theta - tank.angle
            #theta = self.fields.calculateAlpha(tank.angle, theta, 0, time_diff,tank)
            #accel = self.fields.calculateAlpha(current, target, 0, time_diff, tank)
            command = Command(tank.index,self.throttle*math.sqrt(totalY**2+totalX**2),theta,True)
            self.commands.append(command)
    
            '''should we log these results?'''
            self.bzrc.do_commands(self.commands)
    
    
    def huntEnemies(self,tank,enemies,time_diff):
            totalX = 0
            totalY = 0
            '''could add code here  Need to go and get the flag, and if you have it come back. also avoid enemies and obstacles etc.'''
            for enemy in enemies:
                if enemy.status == "alive":
                    deltaX,deltaY = self.fields.getAttractiveField(tank,enemy,800,5)        
                    totalX += deltaX
                    totalY += deltaY
                    break
      
            for obstacle in self.obstacles:
               
                deltaX,deltaY = self.fields.getRepulsiveField(tank,obstacle.midpoint, obstacle.distanceToCenter*1.2, obstacle.distanceToCenter)
                #deltaX,deltaY = self.fields.getTangentialField2(tank,obstacle.midpoint, obstacle.distanceToCenter, obstacle.distanceToCenter, "CCW")
                totalX += deltaX
                totalY += deltaY
            
            theta = math.atan2(totalY, totalX)
            theta = theta - tank.angle
      
            command = Command(tank.index,self.throttle*math.sqrt(totalY**2+totalX**2),theta,True)
            self.commands.append(command)
            
           
            self.bzrc.do_commands(self.commands)  
            
          
            
           
    
    def protectBase(self):
        pass
    
    
    def tick(self, time_diff):
        
        """Some time has passed; decide what to do next."""
        if time_diff == 0:
            return
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        
        ''' list of teammates with velocities and position and flag posession etc. '''
        self.mytanks = mytanks
        ''' positions and angle of othertanks '''
        self.othertanks = othertanks
        ''' flags returns list of where the flag is an who possess it. returns none if no tank is holding the flag '''
        self.flags = flags
       
        ''' visible shots '''
        self.shots = shots

        self.enemies = [tank for tank in othertanks if tank.color !=
                        self.constants['team']]

        self.commands = []
        
        
        for tank in mytanks:
            if tank.flag != "-":
                self.returnFlag(tank,flags,time_diff)
            else:
                if flags[3].poss_color == self.constants['team']:
                    self.huntEnemies(tank,self.enemies,time_diff)
                else:
                    self.captureFlag(tank, flags, 3, time_diff)
                        
    def shoot_em(self, tank):
        my_position = Point(tank.x, tank.y)
        
        for enemy in self.othertanks:
            enemy_position = Point(enemy.x, enemy.y)
            
            if my_position.distance(enemy_position) <= self.constants["shotrange"]:
                deltaX, deltaY = my_position.getDeltaXY(enemy_position)
                theta = math.atan2(deltaY, deltaX)
                theta = theta - tank.angle
                
                if theta < .1 and theta > -.1:
                    line_to_enemy = Line(my_position, enemy_position)
                    
                    safe = True
                    for teamMate in self.mytanks:
                        teamMate_position = Point(teamMate.x, teamMate.y)
                        
                        if teamMate_position.distanceToLine(line_to_enemy) > 10:
                            safe = False
                            break
                    
                    if safe == True:
                        return True
                        
        return False

    
""" A class to perform the potential field and controller calculations
    problem is we need to pass in elapsedtimes and spread and radius, etc.
    my thoughts are to create different instances of this with there own spread and radius
    which could represent different goals/obstacles and then we just make a bunch of different Calculations objects
    then they each can be used more loosely in the Agent class itself """
    
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
        derivative = error - oldError
        dt = elapsedTime
        derivative /= dt 
        alpha += self.Kd*derivative
        #update the error on the tank
        tank.oldError = error
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


def main():
    # Process CLI arguments.
    try:
        execname, host, port = sys.argv
    except ValueError:
        execname = sys.argv[0]
        print >>sys.stderr, '%s: incorrect number of arguments' % execname
        print >>sys.stderr, 'usage: %s hostname port' % sys.argv[0]
        sys.exit(-1)

    # Connect.
    #bzrc = BZRC(host, int(port), debug=True)
    #bzrc = BZRC(host, int(port))
    bzrc = BZRC(host, 35001)
    agent = PFAgent(bzrc)

    prev_time = time.time()

    # Run the agent
    
    try:
        while True:
            time_diff = time.time() - prev_time
            prev_time = time.time()
            agent.tick(time_diff)
            
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()


if __name__ == '__main__':
    main()
