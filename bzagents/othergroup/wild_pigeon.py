#!/usr/bin/python -tt

#####################
#
#logic for clay pigeons: one wild(unpredictable) and one stationary. The one moving predictably is in the pigeon.py file.
#
#####################
import sys
import math
import time

from bzrc import BZRC, Command

def normalize_angle(angle):
	"""Make any angle be between +/- pi."""
	angle -= 2 * math.pi * int (angle / (2 * math.pi))
	if angle <= -math.pi:
		angle += 2 * math.pi
	elif angle > math.pi:
		angle -= 2 * math.pi
	return angle
		
def outOfRange(pigeon):
	#print str(pigeon.x) + ", "+ str(pigeon.y)
	if pigeon.x > 100:
		return (True, "right")
	elif pigeon.x < -100:
		return (True, "left")
	elif pigeon.y > 250:
		return (True, "top")
	elif pigeon.y < -250:
		return (True, "bottom")
	return (False, "inrange")

class WildPigeonAgent(object):
	"""Class handles all command and control logic for a wild clay pigeon tank team."""

	def __init__(self, bzrc):
		self.bzrc = bzrc
		self.constants = self.bzrc.get_constants()
		self.commands = []

	#time diff is in seconds and is a float
	def tick(self, time_diff):
		mytanks, othertanks, flags, shots, obstacles, bases = self.bzrc.get_lots_o_stuff()
		#---------------------MAIN LOGIC AREA------------------------
		
		for tank in mytanks:
			out_of_range, direction = outOfRange(tank)
			if out_of_range:
				target_angle = math.atan2(0 - tank.y, 0 - tank.x)
				relative_angle = normalize_angle(target_angle - tank.angle)
				if(abs(relative_angle) > .7):
					self.commands.append(Command(tank.index, .2, 2*relative_angle, False))
				else:
					self.commands.append(Command(tank.index, 1, 0, False))
			else:
				# speed 1 for 5 seconds, turning one way.
				if time_diff % 10 < 5:
					self.commands = []
					for x in range(0, len(mytanks)):
						self.commands.append(Command(x, 1, .5, False))
				#speed .5 for 4 seconds, turning other way.
				elif time_diff % 10 < 9:
					self.commands = []
					for x in range(0, len(mytanks)):
						self.commands.append(Command(x, .5, -1, False))
		

		results = self.bzrc.do_commands(self.commands)


class SittingPigeonAgent(object):
	"""Class handles all command and control logic for a stationary clay pigeon tank team (aka, none)."""

	def __init__(self, bzrc):
		self.bzrc = bzrc
		self.constants = self.bzrc.get_constants()
		self.commands = []
		self.aliveTime = 0
		self.prevTime = 0
		

	#time diff is in seconds and is a float
	def tick(self, time_diff):
		mytanks, othertanks, flags, shots, obstacles, bases = self.bzrc.get_lots_o_stuff()
		"""don't do anything, just sit there."""
		for tank in mytanks:
			out_of_range, direction = outOfRange(tank)
			if tank.status =="dead":
				self.aliveTime = 0
				self.prevTime = time_diff
			else:
				self.aliveTime = time_diff-self.prevTime
			if out_of_range and self.aliveTime < 10.0:
				target_angle = math.atan2(0 - tank.y, 0 - tank.x)
				relative_angle = normalize_angle(target_angle - tank.angle)
				if(abs(relative_angle) > .5):
					print ">"
					self.commands.append(Command(tank.index, 0, relative_angle*2, False))
				else:
					print "not"
					self.commands.append(Command(tank.index, .3, 0, False))
			else:
				print "stopping"
				self.commands.append(Command(tank.index, 0, 0, False))
		results = self.bzrc.do_commands(self.commands)

def main():
	# Process CLI arguments.
	try:
		execname, host, port = sys.argv
	except ValueError:
		execname = sys.argv[0]
		print >>sys.stderr, '%s: incorrect number of arguments' % execname
		print >>sys.stderr, 'usage: %s hostname port' % sys.argv[0]
		sys.exit(-1)
		
	bzrc = BZRC(host, int(port))
	agent = WildPigeonAgent(bzrc)

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
