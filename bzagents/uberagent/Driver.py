'''
Created on Jun 12, 2014

@author: dml66
'''
from BayesAgent import BayesAgent
from SuperUberAgent import SuperUberAgent
import sys
from bzrc import BZRC
from OccGrid import OccGrid
from ObstacleList import ObstacleList

class Driver(object):
    
    def __init__(self):
        self.grid  = OccGrid(800,800,.1025)
        self.obsList = ObstacleList(self.grid)
        self.tanks = []
        
    def tick(self,tanks,bzrc):
        
        mytanks = bzrc.get_mytanks()
        corners = self.obsList.getObstaclePoints()
        
       
                
        for i in range(len(tanks)):
            tanks[i].update(mytanks[i])
        
        if self.tanks[9].tank.status != "dead":
            self.grid = self.tanks[9].grid
            
        for i in range(len(tanks)):                
            if tanks[i].__class__.__name__ == "SuperUberAgent":
                tanks[i].updateObstacles(corners)
            tanks[i].tick()
        

    
    
    def main(self):
        
        # Process CLI arguments.
        try:
            execname, host, port  = sys.argv
        except ValueError:
            execname = sys.argv[0]
            print >>sys.stderr, '%s: incorrect number of arguments' % execname
            print >>sys.stderr, 'usage: %s hostname port' % sys.argv[0]
            sys.exit(-1)
    
        # Connect.
        
        bzrc = BZRC(host, int(port))
        mytanks = bzrc.get_mytanks()
        for i in range(len(mytanks)):
            if i < 8:
                if i < 5:
                    self.tanks.append(SuperUberAgent(bzrc,mytanks[i],"a"))
                else:
                    self.tanks.append(SuperUberAgent(bzrc,mytanks[i],"d"))  
            else:
                self.tanks.append(BayesAgent(bzrc,mytanks[i],self.grid, self.obsList))
        
           
        try:
            while True:
                self.tick(self.tanks,bzrc)
               
        except KeyboardInterrupt:
            print "Exiting due to keyboard interrupt."
            bzrc.close()
    


if __name__ == '__main__':
    d = Driver()
    d.main()
    
