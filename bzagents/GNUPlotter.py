from __future__ import division

import math
import sys
import time

from itertools import cycle
from PFAgent import Calculations

class Blank(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

try:
    from numpy import linspace
except ImportError:
    # This is stolen from numpy.  If numpy is installed, you don't
    # need this:
    def linspace(start, stop, num=50, endpoint=True, retstep=False):
        """Return evenly spaced numbers.

        Return num evenly spaced samples from start to stop.  If
        endpoint is True, the last sample is stop. If retstep is
        True then return the step value used.
        """
        num = int(num)
        if num <= 0:
            return []
        if endpoint:
            if num == 1:
                return [float(start)]
            step = (stop-start)/float((num-1))
            y = [x * step + start for x in xrange(0, num - 1)]
            y.append(stop)
        else:
            step = (stop-start)/float(num)
            y = [x * step + start for x in xrange(0, num)]
        if retstep:
            return y, step
        else:
            return y


# Constants
# Output file:
FILENAME = 'myPlot.gpi'
# Size of the world (one of the "constants" in bzflag):
WORLDSIZE = 800
# How many samples to take along each dimension:
SAMPLES = 50
# Change spacing by changing the relative length of the vectors.  It looks
# like scaling by 0.75 is pretty good, but this is adjustable:
VEC_LEN = 0.75 * WORLDSIZE / SAMPLES

OBSTACLES = [((150.0, 150.0), (150.0, 90.0), (90.0, 90.0), (90.0, 150.0)),
                ((150.0, 210.0), (150.0, 150.0), (90.0, 150.0), (90.0, 210.0)),
                ((210.0, 150.0), (210.0, 90.0), (150.0, 90.0), (150.0, 150.0)),
                ((150.0, -90.0), (150.0, -150.0), (90.0, -150.0), (90.0, -90.0)),
                ((210.0, -90.0), (210.0, -150.0), (150.0, -150.0), (150.0, -90.0)),
                ((150.0, -150.0), (150.0, -210.0), (90.0, -210.0), (90.0, -150.0)),
                ((-90.0, -90.0), (-90.0, -150.0), (-150.0, -150.0), (-150.0, -90.0)),
                ((-90.0, -150.0), (-90.0, -210.0), (-150.0, -210.0), (-150.0, -150.0)),
                ((-150.0, -90.0), (-150.0, -150.0), (-210.0, -150.0), (-210.0, -90.0)),
                ((-90.0, 150.0), (-90.0, 90.0), (-150.0, 90.0), (-150.0 ,150.0)),
                ((-90.0, 210.0), (-90.0, 150.0), (-150.0, 150.0), (-150.0, 210.0)),
                ((-150.0, 150.0), (-150.0, 90.0), (-210.0, 90.0), (-210.0, 150.0)),
                ((10.0, 60.0), (10.0, -60.0), (-10.0, -60.0), (-10.0, 60.0))]
                
MIDPOINTS = [(120.0, 120.0), (120.0, 180.0), (180.0, 120.0), (120.0, -120.0), (180.0, -120.0), (120.0, -180.0), (-120.0, -120.0), (-120.0, -180.0), (-180.0, -120.0), (-120.0, 120.0), (-120.0, 180.0), (-180.0, 120.0), (0.0, 0.0)]


def gpi_point(x, y, vec_x, vec_y):
    '''Create the centered gpi data point (4-tuple) for a position and
    vector.  The vectors are expected to be less than 1 in magnitude,
    and larger values will be scaled down.'''
    r = (vec_x ** 2 + vec_y ** 2) ** 0.5
    if r > 1:
        vec_x /= r
        vec_y /= r
    return (x - vec_x * VEC_LEN / 2, y - vec_y * VEC_LEN / 2,
            vec_x * VEC_LEN, vec_y * VEC_LEN)


def gnuplot_header(minimum, maximum):
    '''Return a string that has all of the gnuplot sets and unsets.'''
    s = ''
    s += 'set xrange [%s: %s]\n' % (minimum, maximum)
    s += 'set yrange [%s: %s]\n' % (minimum, maximum)
    # The key is just clutter.  Get rid of it:
    s += 'unset key\n'
    # Make sure the figure is square since the world is square:
    s += 'set size square\n'
    # Add a pretty title (optional):
    #s += "set title 'Potential Fields'\n"
    return s
 
def draw_line(p1, p2):
    '''Return a string to tell Gnuplot to draw a line from point p1 to
    point p2 in the form of a set command.'''
    x1, y1 = p1
    x2, y2 = p2
    return 'set arrow from %s, %s to %s, %s nohead lt 3\n' % (x1, y1, x2, y2) 


def draw_obstacles(obstacles):
    '''Return a string which tells Gnuplot to draw all of the obstacles.'''
    s = 'unset arrow\n'

    for obs in obstacles:
        last_point = obs[0]
        for cur_point in obs[1:]:
            s += draw_line(last_point, cur_point)
            last_point = cur_point
        s += draw_line(last_point, obs[0])
    return s
    
def getTotalDeltaXY(x, y):
    
    calc = Calculations()
    
    totalDeltaX = 0
    totalDeltaY = 0
    
    tank = Blank(x, y)
    flag = Blank(0.0, -370.0)
    deltaX,deltaY = calc.getAttractiveField(tank, flag, 800, 1)
    totalDeltaX += deltaX
    totalDeltaY += deltaY
    
    #the "L"s
    for i in range(12):
        ox, oy = MIDPOINTS[i]
        obstacle = Blank(ox, oy)
        deltaX, deltaY = calc.getTangentialField2(tank,obstacle, 42, 42, "CCW")
        totalDeltaX += deltaX
        totalDeltaY += deltaY
        
    #the obstacle in the middle
    ox, oy = MIDPOINTS[12]
    obstacle = Blank(ox, oy)
    deltaX, deltaY = calc.getTangentialField2(tank,obstacle, 60, 60, "CCW")
    totalDeltaX += deltaX
    totalDeltaY += deltaY
    
    return totalDeltaX, totalDeltaY
    
    
def plot_field():
    '''Return a Gnuplot command to plot a field.'''
    
    s = "plot '-' with vectors head\n"

    separation = WORLDSIZE / SAMPLES
    end = WORLDSIZE / 2 - separation / 2
    start = -end

    points = ((x, y) for x in linspace(start, end, SAMPLES)
                for y in linspace(start, end, SAMPLES))

    for x, y in points:
        
        deltaX, deltaY = getTotalDeltaXY(x, y)
        
        plotvalues = gpi_point(x, y, deltaX, deltaY)
        if plotvalues is not None:
            x1, y1, x2, y2 = plotvalues
            s += '%s %s %s %s\n' % (x1, y1, x2, y2)
            
    
    s += 'e\n'
    return s

outfile = open(FILENAME, 'w')
print >>outfile, gnuplot_header(-WORLDSIZE / 2, WORLDSIZE / 2)
print >>outfile, draw_obstacles(OBSTACLES)
print >>outfile, plot_field()

