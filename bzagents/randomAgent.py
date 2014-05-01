import sys
import math
import time
import random

from bzrc import BZRC, Command

class RandomAgent(object):
	
	def __init__(self, bzrc):
		self.bzrc = bzrc
		self.constants = self.bzrc.get_constants()
		self.commands = []
		self.shoot_threshold = 0.5
		self.rotate_sleep_time = 4
		
	def stop_tank(self, tank):
		command = Command(tank.index, 0, 0, False)
		self.commands.append(command)
		
	def full_throttle(self, tank):
		self.bzrc.speed(tank.index, 1)
		
	def random_throttle(self, tank):
		random_speed = random.random()
		
		if random.random < .5:
			random_speed = random_speed * -1.0
			
		self.bzrc.speed(tank.index, random_speed)
		
	def start_random_rotate(self, tank):
		rotate_speed = random.random()
		self.bzrc.angvel(tank.index, rotate_speed)
		
	def stop_rotate(self, tank):
		self.bzrc.angvel(tank.index, 0)
		
	def random_shoot(self, tank):
		random_value = random.random()
		
		if random_value > self.shoot_threshold:
			self.bzrc.shoot(tank.index)
		
	def normalize_angle(self, angle):
		angle -= 2 * math.pi * int (angle / (2 * math.pi))
		if angle <= -math.pi:
			angle += 2 * math.pi
		elif angle > math.pi:
			angle -= 2 * math.pi
		return angle
		
	'''Agent API (public methods)'''
		
	def move_zero(self, x, y):
		self.commands = []
		my_tanks = self.bzrc.get_mytanks()
		tank = my_tanks[0]
		
		self.move_to_position(tank, x, y)
		
		results = self.bzrc.do_commands(self.commands)
		
	def stop_all_tanks(self):
		self.commands = []
		my_tanks = self.bzrc.get_mytanks()
		
		for tank in my_tanks:
			self.stop_tank(tank)
			
		results = self.bzrc.do_commands(self.commands)
		
	def all_random_throttle(self):
		my_tanks = self.bzrc.get_mytanks()
		
		for tank in my_tanks:
			self.random_throttle(tank)
		
	def full_throttle_all_tanks(self):
		my_tanks = self.bzrc.get_mytanks()
		
		for tank in my_tanks:
			self.full_throttle(tank)
		
	def all_random_rotate(self):
		my_tanks = self.bzrc.get_mytanks()
		
		rotate_time = random.randrange(1, 7)
		
		for tank in my_tanks:
			self.start_random_rotate(tank)
		
		time.sleep(rotate_time)
		
		for tank in my_tanks:
			self.stop_rotate(tank)
		
	def all_random_shoot(self):
		my_tanks = self.bzrc.get_mytanks()
		
		for tank in my_tanks:
			self.random_shoot(tank)
		
		
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

	agent = RandomAgent(bzrc)

	prev_time = time.time()

	# Run the agent
	try:
		
		while True:
			agent.all_random_throttle()
			agent.all_random_rotate()
			agent.all_random_shoot()
		
	except KeyboardInterrupt:
		print "Exiting due to keyboard interrupt."
		bzrc.close()
		
		
if __name__ == '__main__':
	main()
