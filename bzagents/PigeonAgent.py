import sys
import math
import time
import random

from bzrc import BZRC, Command

class PigeonAgent(object):
    
    def __init__(self, bzrc, mode, time):
        self.bzrc = bzrc
        self.mode = mode
        self.num_tanks = 1
        self.cur_time = time
        
        self.const_velocity = .5
        
        self.time_move = self.cur_time
        self.time_turn = self.cur_time
        
        self.move_interval = 5.0
        self.turn_interval = 2.0
        
    def behave(self, time):
        if self.mode == "sit":
            return
        elif self.mode == "const":
            #self.mytanks = self.bzrc.get_mytanks()
            for i in range(self.num_tanks):
                self.bzrc.speed(i, self.const_velocity)
        elif self.mode == "wild":
            for i in range(self.num_tanks):
                #self.mytanks = self.bzrc.get_mytanks()
                if (time - self.time_move) > self.move_interval:
                    for i in range(self.num_tanks):
                        speed = self.getRandomSpeed()
                        self.bzrc.speed(i, speed)
                    self.time_move = time
                    
                if (time - self.time_turn) > self.turn_interval:
                    for i in range(self.num_tanks):
                        angvel = self.getRandomAngvel()
                        self.bzrc.angvel(i, angvel)
                    self.time_turn = time
                        
    def getRandomAngvel(self):
        rval = random.random()
        rval *= self.getDirection()
        return rval
        
    def getDirection(self):
        threshold = .25
        
        n = random.random()
        if n <= threshold:
            direction = -1.0
        else:
            direction = 1.0
        
        return direction
        
    def getRandomSpeed(self):
        rval = random.random()
        rval *= self.getDirection()
        return rval
        
    def stop(self):
        for tank in self.bzrc.get_mytanks():
            self.bzrc.speed(tank.index, 0)
            self.bzrc.angvel(tank.index, 0)
    
    
def main():
    # Process CLI arguments.
    try:
        execname, host, port, mode = sys.argv
    except ValueError:
        execname = sys.argv[0]
        print >>sys.stderr, '%s: incorrect number of arguments' % execname
        print >>sys.stderr, 'usage: %s hostname port [sit|const|wild]' % sys.argv[0]
        sys.exit(-1)

    bzrc = BZRC(host, int(port))
    cur_time = time.time()
    
    agent = PigeonAgent(bzrc, mode, cur_time)

    # Run the agent
    try:
        
        while True:
            cur_time = time.time()
            agent.behave(cur_time)
            
                    
                
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        agent.stop()
        bzrc.close()
        
        
        
if __name__ == '__main__':
    main()
