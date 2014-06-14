'''
Created on Jun 14, 2014

@author: dml66
'''
import math
from geo import Point
import numpy as np
t = .5
class Kalman(object):
    def __init__ (self,enemyx,enemyy):
        self.enemy = Point(enemyx,enemyy)
        self.F = np.matrix([[1,t,(.5*(t**2)),0,0,0],
                            [0,1,t,0,0,0],
                            [0,0,1,0,0,0],
                            [0,0,0,1,t,(.5*(t**2))],
                            [0,0,0,0,1,t],
                            [0,0,0,0,0,1]])
        self.SigmaS = np.matrix([[.1,0,0,0,0,0],
                                [0,.1,0,0,0,0,],
                                [0,0,50,0,0,0],
                                [0,0,0,.1,0,0],
                                [0,0,0,0,.1,0],
                                [0,0,0,0,0,50]])
        self.H = np.matrix([[1,0,0,0,0,0],
                            [0,0,0,1,0,0]])
        self.SigmaE = np.matrix([[25,0],[0,25]])
        self.FTrans = self.F.transpose()
        self.HTrans = self.H.transpose()
        self.MuKnot = np.matrix([[enemyx],[0],[0],[enemyy],[0],[0]])
        self.SigmaKnot = np.matrix([[100,0,0,0,0,0],
                                    [0,.1,0,0,0,0],
                                    [0,0,.1,0,0,0],
                                    [0,0,0,100,0,0],
                                    [0,0,0,0,.1,0],
                                    [0,0,0,0,0,.1]])
        self.SigmaCurrent = self.SigmaKnot
        self.SigmaPrev = self.SigmaKnot
        self.MuCurrent = self.MuKnot
        self.MuPrev = self.MuKnot
    
    '''runs the filter but predicts out into the future @param iterations down the markov
    chain. Returns the new predicted Mu and Sigma for use in plotting, etc. '''
    def predictiveKalman(self,Mu,Sigma,iterations):
        if(iterations == 0):
            return Mu,Sigma
        else:
            MuNext = self.predictiveMu(Mu)
            SigmaNext = self.predictiveSigma(Sigma)
            iterations = iterations-1
            return self.predictiveKalman(MuNext,SigmaNext,iterations)
            
    ''' runs the kalman filter and returns the mu and sigma
        which is our guess of where the enemy currently is'''
    def runKalman(self,bzrc):
        
        self.MuPrev = self.updateMuCurrent(bzrc)
        
        self.SigmaPrev = self.updateSigmaCurrent()
        
        return self.MuPrev,self.SigmaPrev
                                 
    ''' helper functions to run the equations'''
    def transitionTerm(self):
        return (self.F*self.SigmaPrev*self.FTrans) + self.SigmaS
    
    def predictiveMu(self,Mu):
        return self.F*Mu
    
    def KTimePlusOne(self):
        firstTerm = self.transitionTerm()
        secondTerm = ((self.H*firstTerm*self.HTrans)+self.SigmaE).I
        secondTerm = self.HTrans * secondTerm
        return firstTerm * secondTerm
    
    def updateMuCurrent(self,bzrc):
        firstTerm = self.F*self.MuPrev
        KT = self.KTimePlusOne()
        othertank = self.enemy
        secondTerm = np.matrix([[othertank.x],[othertank.y]]) - (self.H*self.F*self.MuPrev)
        self.MuCurrent = firstTerm + KT*secondTerm
        return self.MuCurrent
    
    def updateSigmaCurrent(self):
        identity = np.identity(6)
        firstTerm = identity - (self.KTimePlusOne()*self.H)
        secondTerm = self.transitionTerm()
        self.SigmaCurrent = firstTerm * secondTerm
        return self.SigmaCurrent
        
    def predictiveTrans(self,Sigma):
        return (self.F*Sigma*self.FTrans) + self.SigmaS    
        
    def predictiveKTime(self,Sigma):
        firstTerm = self.predictiveTrans(Sigma)
        secondTerm = ((self.H*firstTerm*self.HTrans)+self.SigmaE).I
        secondTerm = self.HTrans * secondTerm
        return firstTerm * secondTerm
        
    def predictiveSigma(self,Sigma):
        identity = np.identity(6)
        firstTerm = identity - (self.predictiveKTime(Sigma)*self.H)
        secondTerm = self.predictiveTrans(Sigma)
        Sigma = firstTerm * secondTerm
        return Sigma
        
    def reset(self):
        self.SigmaCurrent = self.SigmaKnot
        self.SigmaPrev = self.SigmaKnot
        self.MuCurrent = self.MuKnot
        self.MuPrev = self.MuKnot
