'''
Created on May 1, 2014

@author: dml66
'''

import sys
import math
import time

from bzrc import BZRC, Command

class PFAgent(object):
    
    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        self.throttle = .25
        self.obstacles = bzrc.get_obstacles()
        self.fields = Calculations()
        
    
    def tick(self, time_diff):
        print "the diff" , time_diff
        """Some time has passed; decide what to do next."""
        if time_diff == 0:
            return
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        
        ''' list of teammates with velocities and position and flag posession etc. '''
        self.mytanks = mytanks
        ''' positions and angle of othertanks '''
        self.othertanks = othertanks
        ''' flags returns list of where the falg is an who possess it. returns none if no tank is holding the flag '''
        self.flags = flags
        ''' visible shots '''
        self.shots = shots

        self.enemies = [tank for tank in othertanks if tank.color !=
                        self.constants['team']]

        self.commands = []
        i = 0
        for tank in mytanks:
            totalX = 0
            totalY = 0
            '''could add code here  Need to go and get the flag, and if you have it come back. also avoid enemies and obstacles etc.'''
            tank.oldError = 0
            if (i % 2) == 0:
                deltaX,deltaY = self.fields.getAttractiveField(tank, flags[1], tank.oldError, time_diff, 800, 1)
            else:
                deltaX,deltaY = self.fields.getAttractiveField(tank, flags[2], tank.oldError, time_diff, 800, 1)
            totalX += deltaX
            totalY += deltaY
            i += 1
            for obstacle in self.obstacles:
               
                '''deltaX,deltaY = self.fields.getRepulsiveField(tank,obstacle,tank.oldError,time_diff, 50,10)
                totalX += deltaX
                totalY += deltaY'''
            '''can also calculate a repulsion for enemies'''
            for enemy in self.enemies:             
                deltaX,deltaY = self.fields.getRepulsiveField(tank, enemy, tank.oldError, time_diff, 15, 1)
                totalX += deltaX
                totalY += deltaY
            print "deltaX" , totalX
            print "deltaY" , totalY
            theta = math.atan2(totalY, totalX)
            theta = theta - tank.angle
            print "theta" , theta
            command = Command(tank.index,self.throttle*abs(totalY+totalX),theta,False)
            self.commands.append(command)
        #command = Command(tank.index,)
        # self.attack_enemies(tank)
            
        '''should we log these results?'''
        results = self.bzrc.do_commands(self.commands)

    def attack_enemies(self, tank):
        """Find the closest enemy and chase it, shooting as you go."""
        best_enemy = None
        best_dist = 2 * float(self.constants['worldsize'])
        for enemy in self.enemies:
            if enemy.status != 'alive':
                
                continue
            dist = math.sqrt((enemy.x - tank.x)**2 + (enemy.y - tank.y)**2)
            if dist < best_dist:
                best_dist = dist
                best_enemy = enemy
        if best_enemy is None:
            ''' constructor for Command(index,speed,angular,shoot)'''
            command = Command(tank.index, 0, 0, False)
            self.commands.append(command)
        else:
            self.move_to_position(tank, best_enemy.x, best_enemy.y)

    def move_to_position(self, tank, target_x, target_y):
        """Set command to move to given coordinates."""
        target_angle = math.atan2(target_y - tank.y,
                                  target_x - tank.x)
        relative_angle = self.normalize_angle(target_angle - tank.angle)
        command = Command(tank.index, 1, 2 * relative_angle, True)
        self.commands.append(command)
        

    def normalize_angle(self, angle):
        """Make any angle be between +/- pi."""
        angle -= 2 * math.pi * int (angle / (2 * math.pi))
        if angle <= -math.pi:
            angle += 2 * math.pi
        elif angle > math.pi:
            angle -= 2 * math.pi
        return angle
    
    
  
    
""" A class to perform the potential field and controller calculations
    problem is we need to pass in elapsedtimes and spread and radius, etc.
    my thoughts are to create different instances of this with there own spread and radius
    which could represent different goals/obstacles and then we just make a bunch of different Calculations objects
    then they each can be used more loosely in the Agent class itself """
    
class Calculations(object):
    def __init__ (self):
        self.Kp = .1
        self.Kd = .5
     
    ''' The PD controller calculations'''
    def calculateAlpha(self,tank,target,oldError,elapsedTime):
        '''tank has x,y,angle,etc. use bzrc to see the tank'''
        # y(t) - x(t) is error
        error = (target.y - tank.y) + (target.x - tank.x)
        alpha = self.Kp*error
        derivative = error - oldError
        dt = elapsedTime
        derivative /= dt 
        alpha += self.Kd*derivative
        #update the error on the tank
        tank.oldError = error
        return 1 # return alpha here when it works
    
    def distance(self, tank,target):
        distance = math.sqrt((target.x-tank.x)**2 + (target.y-tank.y)**2)
        return distance
    
    def angle(self,tank,target):
        angle = math.atan2((target.y-tank.y),(target.x-tank.x))
        return angle
    
    """ returns the change in x and y for an attractive field, """
    def getAttractiveField(self,tank,target,oldError,elapsedTime,spread,radius):
        alpha = self.calculateAlpha(tank, target, oldError, elapsedTime)
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
    def getRepulsiveField(self,tank,target,oldError,elapsedTime,spread,radius):
        alpha = self.calculateAlpha(tank, target, oldError, elapsedTime)
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



    #target is a Line object
    def getTangentialObstacleField(self, tank, target, oldTank, elapsedTime):
        
        deltaX = 0.0
        deltaY = 0.0
        

        tankPosition = Point(tank.x, tank.y)
        closestPoint = tankPosition.closestPointOnLine(target.p1, target.p2)
        
        if self.distance(tankPosition, closestPoint) < target.spread:
            lineToTarget = Line(tankPosition, closestPoint)
            if target.isPerpendicular(lineToTarget):

                midpoint = target.getMidpoint()   
    
    
    def getTangentialField2(self,tank,target,oldError,elapsedTime,spread,radius,direction):
        alpha = self.calculateAlpha(tank, target, oldError, elapsedTime)
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
            
                midpoint = target.getMidpoint()
                if closestPoint.x < midpoint.x:
                    deltaX = -1.0
                elif closestPoint.x > midpoint.x:
                    deltaX = 1.0
                else:
                    deltaX = 0.0
                    
                if closestPoint.y < midpoint.y:
                    deltaY = -1.0
                elif closestPoint.y > midpoint.y:
                    deltaY = 1.0
                else:
                    deltaY = 0.0
           
                    
        return deltaX, deltaY


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
    bzrc = BZRC(host, 39491)
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
