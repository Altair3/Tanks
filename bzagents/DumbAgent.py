import sys
import math
import time
import random

from bzrc import BZRC, Command

class DumbAgent(object):
    
    def __init__(self, bzrc, tank, cur_time):
        self.tank = tank
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.last_move_time = cur_time
        self.last_shoot_time = cur_time
        self.last_rotate_time = cur_time
        self.is_moving = False
        self.is_rotating = False
        self.shoot_interval = 2
        
    def stop_tank(self):
        self.bzrc.speed(self.tank.index, 0)
        self.bzrc.angvel(self.tank.index, 0)
        self.is_moving = False
        self.is_rotating = False
        
    def full_throttle(self, cur_time):
        self.bzrc.speed(self.tank.index, 1)
        self.is_moving = True
        self.last_move_time = cur_time
        
    def start_left_rotate(self, cur_time):
        self.bzrc.angvel(self.tank.index, 1)
        self.is_rotating = True
        self.last_rotate_time = cur_time
        
    def stop_rotate(self):
        self.bzrc.angvel(self.tank.index, 0)
        self.is_rotating = False
        
    def shoot(self):
        self.bzrc.shoot(self.tank.index) 
        
    def normalize_angle(self, angle):
        angle -= 2 * math.pi * int (angle / (2 * math.pi))
        if angle <= -math.pi:
            angle += 2 * math.pi
        elif angle > math.pi:
            angle -= 2 * math.pi
        return angle  
        
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
    
    agent_list = []
    
    for tank in bzrc.get_mytanks():
        agent_list.append(DumbAgent(bzrc, tank, time.time()))
    
    move_time = 4

    # Run the agent
    try:
        
        while True:
            cur_time = time.time()
            
            for agent in agent_list:
                
                if agent.is_moving == False and agent.is_rotating == False:
                    agent.full_throttle(cur_time)
                
                if agent.is_moving == True:
                    if (cur_time - agent.last_move_time) >= move_time:
                        agent.stop_tank()
                        move_time = random.randrange(3,8)
                
                if agent.is_rotating == False and agent.is_moving == False:
                    agent.start_left_rotate(cur_time)
                    
                if agent.is_rotating == True:
                    if (cur_time - agent.last_rotate_time) >= 1.5:
                        agent.stop_tank()
                
                if (cur_time - agent.last_shoot_time) >= agent.shoot_interval:
                    agent.shoot()
                    agent.shoot_interval = (random.randrange(2, 3) - .5)
                    
                
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        for agent in agent_list:
            agent.stop_tank()
        bzrc.close()
        
        
if __name__ == '__main__':
    main()
