

import sys
import math
import time

import random
from bzrc import BZRC, Command
from math import pi

class Agent(object):
    """Class handles all command and control logic for a teams tanks."""

    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        self.pigeonDirections = []
        self.pigeonSpeeds = []
        self.lastTimeUpdated = -1

	#time diff is in seconds and is a float
    def tick(self, time_diff):
		second = int(time_diff)
		if second == self.lastTimeUpdated:
			return
		self.lastTimeUpdated = second
		
		"""Some time has passed; decide what to do next."""
		mytanks, othertanks, flags, shots, obstacles, bases = self.bzrc.get_lots_o_stuff()
		self.mytanks = mytanks
		self.othertanks = othertanks
		self.flags = flags
		self.shots = shots
		self.obstacles = obstacles
		self.bases = bases
		self.enemies = [tank for tank in othertanks if tank.color !=
						self.constants['team']]
		#---------------------MAIN LOGIC AREA------------------------

		#set up pigeon directions if needed
		if len(self.pigeonDirections) == 0:
			for x in range(0, len(mytanks)):
				self.pigeonDirections.append(getRandomDirection())
				self.pigeonSpeeds.append(getRandomSpeed())
        
		self.commands = []
		for i in range(0, len(mytanks)):
			#if the pigeon is aimed in the correct direction
			#print "angle" + str(mytanks[i].angle) + "    direct:" + str(self.pigeonDirections[i])
			if( (mytanks[i].angvel == 0 and mytanks[i].vx != 0)			or
				abs(mytanks[i].angle - self.pigeonDirections[i]) < .5   or
				abs(mytanks[i].angle - self.pigeonDirections[i] + 2*pi) < .5):
				self.commands.append(Command(i, self.pigeonSpeeds[i], 0, False))
				
			#if the pigeon needs to be rotated into the proper direction
			else:			
				#makes sure the speed is random
				self.pigeonSpeeds[i] = getRandomSpeed()
				angvel = .5
				if self.pigeonDirections[i] > pi:
					angvel = -.5
				
				self.commands.append(Command(i, 0, angvel, False))
        
		
		results = self.bzrc.do_commands(self.commands)
        #---------------------END MAIN LOGIC AREA------------------------
	
def getRandomDirection():
	offset = random.uniform(-.5,0)
	#offset = -.2
	return pi + offset

def getRandomSpeed():
	return random.uniform(.5,1)



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
    #bzrc contains simply the connection (open the socket, connect to the game)
    bzrc = BZRC(host, int(port))

    agent = Agent(bzrc)

    prev_time = time.time()

    # Run the agent
    try:
        while True:
            time_diff = time.time() - prev_time
            agent.tick(time_diff)
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()


if __name__ == '__main__':
    main()

# vim: et sw=4 sts=4
