'''
Created on May 1, 2014

@author: dml66
'''

import sys
import math
import time

from bzrc import BZRC, Command
from geo import Point, Line

class PFAgent(object):
    
    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        self.hasFlag = False
   
        
    
    def tick(self, time_diff):
        """Some time has passed; decide what to do next."""
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

        for tank in mytanks:
            
            self.attack_enemies(tank)
            
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
     
    
    def calculateAlpha(self,tank,target,oldTank,oldTarget,elapsedTime):
        '''tank has x,y,angle,etc. use bzrc to see the tank'''
        # y(t) - x(t) is error
        error = (target.y - tank.y) + (target.x - tank.x)
        alpha = self.Kp*error
        derivative = error - ((oldTarget.y-oldTank.y) + (oldTarget.x-oldTank.x))
        dt = elapsedTime
        derivative /= dt 
        alpha += self.Kd*derivative
      
        return alpha
    
    def distance(self, tank,target):
        distance = math.sqrt((target.x-tank.x)**2 + (target.y-tank.y)**2)
        return distance
    
    def angle(self,tank,target):
        angle = math.atan2((target.y-tank.y),(target.x-tank.x))
        return angle
    
    """ returns the change in x and y for an attractive field, """
    def getAttractiveField(self,tank,target,oldTank,oldTarget,elapsedTime,spread,radius):
        alpha = self.calculateAlpha(tank, target, oldTank, oldTarget, elapsedTime)
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
    def getRepulsiveField(self,tank,target,oldTank,oldTarget,elapsedTime,spread,radius):
        alpha = self.calculateAlpha(tank, target, oldTank, oldTarget, elapsedTime)
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
    def getTangentialField(self, tank, target, oldTank, elapsedTime):
        tankPosition = Point(tank.x, tank.y)
        closestPoint = tankPosition.closestPointOnLine(target.p1, target.p2)
        
        if self.distance(tankPosition, closestPoint) < target.spread:
            lineToTarget = Line(tankPosition, closestPoint)
            if target.isPerpendicular(lineToTarget):
                midpoint = target.getMidpoint()
                
                
                
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
    bzrc = BZRC(host, int(port))

    agent = PFAgent(bzrc)
    
    point1 = Point(4.0, 1.1)
    point2 = Point(-2.0, 3.1)
    point3 = Point(-1.0, 0.1)
    
    line1 = Line(point1, point2)
    
    point4 = point3.closestPointOnLine(line1)
    
    line2 = Line(point3, point4)
    
    print line1.getMidpoint().x, line1.getMidpoint().y

    prev_time = time.time()

    # Run the agent
    '''
    try:
        while True:
            time_diff = time.time() - prev_time
            agent.tick(time_diff)
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()
    '''


if __name__ == '__main__':
    main()
