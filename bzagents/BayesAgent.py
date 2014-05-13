import sys
import math
import random
import time
import numpy as np
import Visualizer
from bzrc import BZRC, Command

class BayesAgent(object):
    
    def __init__(self):
        
      
        self.grid = OccGrid(800, 800, .07125) 
        #the .07125 comes from the 4 Ls world where 7.125% of the world was occupied
        init_window(800,800)
        update_grid(self.grid)
        draw_grid()
        
    
    def tick(time_diff):
        pass
        
        #take observations
        #update table    

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
        self.grid.fill(self.prior)
        
    def convert(self, x, y):
        return (self.yMax-y), (x+self.xMax)
        
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
        execname, host, port, enemy = sys.argv
    except ValueError:
        execname = sys.argv[0]
        print >>sys.stderr, '%s: incorrect number of arguments' % execname
        print >>sys.stderr, 'usage: %s hostname port' % sys.argv[0]
        sys.exit(-1)

    # Connect.
    #bzrc = BZRC(host, int(port))
    #agent = BayesAgent(bzrc)
    
    #prev_time = time.time()

    # Run the agent
    
    '''
    try:
        while True:
            time_diff = time.time() - prev_time
            prev_time = time.time()
            agent.tick(time_diff)
            
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()
    '''
    
    '''
    Grid test stuff
    grid = OccGrid(10,10,2)
    
    grid.set(-5,5, 1)
    grid.set(0,5, 1)
    grid.set(5,5, 1)
    grid.set(-5,0, 1)
    grid.set(0,0, 1)
    grid.set(5,0, 1)
    grid.set(-5,-5, 1)
    grid.set(0,-5, 1)
    grid.set(5,-5, 1)
    
    print grid.toString()
    '''


if __name__ == '__main__':
    main()
        