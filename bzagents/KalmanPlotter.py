from __future__ import division

import math
import sys
import time

from itertools import cycle
from KalmanAgent import Calculations

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
FILENAME = 'kalman.gpi'
# Size of the world (one of the "constants" in bzflag):
WORLDSIZE = 800



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
    s += 'set pm3d\n'
    s += 'set view map\n'
    # The key is just clutter.  Get rid of it:
    s += 'unset key\n'
    # Make sure the figure is square since the world is square:
    s += 'set size square\n'
    s += 'set palette model RGB functions 1-gray, 1-gray, 1-gray\n'
    s += 'set isosamples 100\n'
    # Add a pretty title (optional):
    #s += "set title 'Potential Fields'\n"
    return s
 
    
def plot_field(sigmaX,sigmaY,rho):
    '''Return a Gnuplot command to plot a field.'''
    s = ""
    s += 'sigma_x = ' + str(sigmaX) + "\n"
    s += 'sigma_y = ' + str(sigmaY) + "\n"
    s += 'rho = ' + str(rho) + "\n"
    s += 'splot 1.0/(2.0 * pi * sigma_x * sigma_y * sqrt(1 - rho**2))* exp(-1.0/2.0 * (x**2 / sigma_x**2 + y**2 / sigma_y**2-2.0*rho*x*y/(sigma_x*sigma_y) ) ) with pm3d\n'
    #print "sigmaX",sigmaX
    #print "sigmaY",sigmaY
    #print"rho",rho
    return s
    
def plot(sigmaX,sigmaY,rho):
	outfile = open(FILENAME, 'w')
	print >>outfile, gnuplot_header(-WORLDSIZE / 2, WORLDSIZE / 2)
	print >>outfile, plot_field(sigmaX,sigmaY,rho)

