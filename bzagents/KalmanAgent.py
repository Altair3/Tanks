'''
Created on May 29, 2014

@author: dml66
'''

import sys
import math
import random
import time

from bzrc import BZRC, Command
from obstacle import Obstacle
from geo import Point, Line

class KalmanAgent(object):
    
    def __init__(self, bzrc, enemy):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        self.throttle = .15
        self.obstacles = []
        self.filter = Calculations()

    
    def normalize_angle(self, angle):
        """Make any angle be between +/- pi."""
        angle -= 2 * math.pi * int (angle / (2 * math.pi))
        if angle <= -math.pi:
            angle += 2 * math.pi
        elif angle > math.pi:
            angle -= 2 * math.pi
        return angle
        
    def sendCommand(self,totalY,totalX,tank):
        shoot = self.shoot_em(tank)
     
        theta = math.atan2(totalY,totalX)
        theta = self.normalize_angle(theta-tank.angle)
 
        command = Command(tank.index,0,.85*theta,shoot)
        self.commands.append(command)
        self.bzrc.do_commands(self.commands)  
        
    def tick(self, time_diff):
        
        """Some time has passed; decide what to do next."""
        if time_diff == 0:
            return
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        
        ''' list of teammates with velocities and position and flag posession etc. '''
        self.mytanks = mytanks
        ''' positions and angle of othertanks '''
        self.othertanks = othertanks
  

        self.enemies = [tank for tank in othertanks if tank.color !=
                        self.constants['team']]

        self.commands = []
        
        
        for tank in mytanks:
			pass
     
     
     
    
    def shoot_em(self, tank):
        my_position = Point(tank.x, tank.y)
      
                        
        return True                    
                
""" A class to perform the potential field and controller calculations
    problem is we need to pass in elapsedtimes and spread and radius, etc.
    my thoughts are to create different instances of this with there own spread and radius
    which could represent different goals/obstacles and then we just make a bunch of different Calculations objects
    then they each can be used more loosely in the Agent class itself """
    
class Calculations(object):
    def __init__ (self):
        self.Kp = .1
        self.Kd = .2
     
    


def main():
    # Process CLI arguments.
    try:
        execname, host, port, enemy = sys.argv
    except ValueError:
        execname = sys.argv[0]
        print >>sys.stderr, '%s: incorrect number of arguments' % execname
        print >>sys.stderr, 'usage: %s hostname port' % sys.argv[0]
        sys.exit(-1)

    # Connect.
    #bzrc = BZRC(host, int(port), debug=True)
    bzrc = BZRC(host, int(port))
    #bzrc = BZRC(host, 35001)
    agent = PFAgent(bzrc,enemy)

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
