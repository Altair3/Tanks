'''
Created on May 29, 2014

@author: dml66
'''

import sys
import math
import random
import time
import numpy as np
from bzrc import BZRC, Command
from obstacle import Obstacle
from geo import Point, Line
t = .5
class KalmanAgent(object):
    
    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        self.throttle = .15
        self.obstacles = []
        self.Kfilter = Calculations()

    
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
        
    def tick(self):
        
      
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        
        ''' list of teammates with velocities and position and flag posession etc. '''
        self.mytanks = mytanks
        ''' positions and angle of othertanks '''
        self.othertanks = othertanks
  

        self.enemies = [tank for tank in othertanks if tank.color !=
                        self.constants['team']]

        self.commands = []
        
        
        for tank in mytanks:
            
            enemyX,enemyY = self.Kfilter.runKalman(self.bzrc)
            
     

    
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

        self.F = np.matrix([[1,t,(.5*(t**2)),0,0,0],
                            [0,1,t,0,0,0],
                            [0,0,1,0,0,0],
                            [0,0,0,1,t,(.5*(t**2))],
                            [0,0,0,0,1,t],
                            [0,0,0,0,0,1]])
        self.SigmaS = np.matrix([[.1,0,0,0,0,0],
                                [0,.1,0,0,0,0,],
                                [0,0,100,0,0,0],
                                [0,0,0,.1,0,0],
                                [0,0,0,0,.1,0],
                                [0,0,0,0,0,100]])
        self.H = np.matrix([[1,0,0,0,0,0],
                            [0,0,0,1,0,0]])
        self.SigmaE = np.matrix([[25,0],[0,25]])
        self.FTrans = self.F.transpose()
        self.HTrans = self.H.transpose()
        self.MuKnot = np.matrix([[210],[0],[0],[0],[0],[0]])
        self.SigmaKnot = np.matrix([[100,0,0,0,0,0],
                                    [0,1,0,0,0,0],
                                    [0,0,1,0,0,0],
                                    [0,0,0,100,0,0],
                                    [0,0,0,0,1,0],
                                    [0,0,0,0,0,1]])
        self.SigmaCurrent = self.SigmaKnot
        self.SigmaPrev = self.SigmaKnot
        self.MuCurrent = self.MuKnot
        self.MuPrev = self.MuKnot
        
    ''' runs the kalman filter and returns the mu x and mu y
        which is our prediction of where the enemy likely is'''
    def runKalman(self,bzrc):
        
        self.MuPrev = self.updateMuCurrent(bzrc)
        
        self.SigmaPrev = self.updateSigmaCurrent()
        
        return self.MuPrev.item((0,0)),self.MuPrev.item((3,0))
        
        
    '''function for plotting the filter'''
    def covarianceMatrix(self,bzrc):
        sigmaXsquare = self.SigmaCurrent.item((0,0))
        sigmaYsquare = self.SigmaCurrent.item((3,3))
        sigmaX = math.sqrt(sigmaXsquare)
        sigmaY = math.sqrt(sigmaYsquare)
        tank = bzrc.read_othertanks[0]
        X = tank.x
        Y = tank.y
        rho = ((X-self.MuCurrent.item((0,0)))*(Y-self.MuCurrent.item((3,0))))/(sigmaX*sigmaY)
        self.covariance = np.matrix([[sigmaXsquare,(rho*sigmaX*sigmaY)],
                                    [(rho*sigmaX*sigmaY),sigmaYsquare]])
                                    
    
    
                                    
    ''' helper functions to run the equations'''
    def transitionTerm(self):
        return (self.F*self.SigmaPrev*self.FTrans) + self.SigmaS
    
    def KTimePlusOne(self):
        firstTerm = self.transitionTerm()
        secondTerm = ((self.H*firstTerm*self.HTrans)+self.SigmaE).I
        secondTerm = self.HTrans * secondTerm
        return firstTerm * secondTerm
    
    def updateMuCurrent(self,bzrc):
        firstTerm = self.F*self.MuPrev
        KT = self.KTimePlusOne()
        othertank = bzrc.get_othertanks()[0]
        secondTerm = np.matrix([[othertank.x],[othertank.y]]) - (self.H*self.F*self.MuPrev)
        self.MuCurrent = firstTerm + KT*secondTerm
        return self.MuCurrent
    
    def updateSigmaCurrent(self):
        identity = np.identity(6)
        firstTerm = identity - (self.KTimePlusOne()*self.H)
        secondTerm = self.transitionTerm()
        self.SigmaCurrent = firstTerm * secondTerm
        return self.SigmaCurrent
        
    def reset(self):
        self.SigmaCurrent = self.SigmaKnot
        self.SigmaPrev = self.SigmaKnot
        self.MuCurrent = self.MuKnot
        self.MuPrev = self.MuKnot

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
    #bzrc = BZRC(host, 35001)
    agent = KalmanAgent(bzrc)

    prev_time = time.time()

    # Run the agent
    count = 0 
    try:
        while True:
            
            time_diff = time.time() - prev_time
            if(time_diff >= .5):
                prev_time = time.time()              
                agent.tick()
                count += 1
            if (count > 20):
                count = 0 
                agent.Kfilter.reset()    
                
            
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()


if __name__ == '__main__':
    main()
