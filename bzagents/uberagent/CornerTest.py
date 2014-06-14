from geo import Point, Line
from OccGrid import OccGrid
from ObstacleList import ObstacleList
import time

def main():
    grid = OccGrid(800,800,.1)
    
    for x in range(-200, 201):
        for y in range(-200,201):
            grid.set(x, y, .9)
            
    obsList = ObstacleList(grid)
    startTime = time.time()
    obsList.scanGrid(-300,100, 200)
    obsList.scanGrid(-300,100, 200)
    endTime = time.time()
    
    print "Time elapsed:", str(endTime-startTime)
    
    myList = obsList.getObstaclePoints()
    
    print "Corners:"
    for p in myList:
        print "(" + str(p.x) + "," + str(p.y) + ")"
    
    
if __name__ == '__main__':
    main()
    

    
    
            
    
