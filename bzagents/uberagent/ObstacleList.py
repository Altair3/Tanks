from OccGrid import OccGrid
from geo import Point,Line

class ObstacleList(object):
    
    def __init__(self, occgrid):
        
        self.occgrid = occgrid
        
        self.yMax = occgrid.yMax
        self.yMin = self.yMax * -1
        self.xMax = occgrid.xMax
        self.xMin = self.xMax * -1
        
        self.daList = []
        self.threshold = .6
        self.neighborCheckNumber = 1
        
    def getObstaclePoints(self):
        return self.daList
        
    def removeCornersInBlock(self, x, y, length):
        
        for p in self.daList:
            pX = p.x
            pY = p.y
            
            if (pX <= (x+length)) and (pX >= x):
                if (pY <= (y+length)) and (pY >= y):
                    self.daList.remove(p)
        
    def scanGrid(self, startX, startY, length):
        
        self.removeCornersInBlock(startX, startY, length)
        
        for x in range(startX, (startX+length+1)):
            for y in range(startY, (startY+length+1)):
                if (x < self.xMin) or (x > self.xMax) or (y < self.yMin) or (y > self.yMax):
                    continue
                #print "Scanning:", "(" + str(x) + "," + str(y) + ")"
                if self.isCorner(x,y):
                    self.daList.append(Point(x,y))
        
    def isCorner(self, x, y):
        
        if self.occgrid.get(x, y) >= self.threshold:
            
            up = self.checkUp(x,y)
            down = self.checkDown(x,y)
            left = self.checkLeft(x,y)
            right = self.checkRight(x,y)
            
            if (up and left):
                if ((not down) and (not right)):
                    return True
                else:
                    return False
            
            if (up and right):
                if ((not down) and (not left)):
                    return True
                else:
                    return False
                    
            if (down and left):
                if ((not up) and (not right)):
                    return True
                else:
                    return False
                    
            if (down and right):
                if ((not up) and (not left)):
                    return True
                else:
                    return False
            
        return False
        
    def checkUp(self, x, y):
        number = 0
        for i in range(1, self.neighborCheckNumber+1):
            if (y + i) <= self.yMax:
                prob = self.occgrid.get(x, (y+i))
                
                if prob < self.threshold:
                    return False
                
        return True
        
    def checkDown(self, x, y):
        for i in range(self.neighborCheckNumber, 0, -1):
            if (y - i) >= self.yMin:
                prob = self.occgrid.get(x, (y-i))
                
                if prob < self.threshold:
                    return False
                
        return True
        
    def checkRight(self, x, y):
        for i in range(1, self.neighborCheckNumber+1):
            if (x + i) <= self.xMax:
                prob = self.occgrid.get((x+i), y)
                
                if prob < self.threshold:
                    return False
                
        return True
        
    def checkLeft(self, x, y):
        for i in range(self.neighborCheckNumber, 0, -1):
            if (x - i) >= self.xMin:
                prob = self.occgrid.get((x-i), y)
                if prob < self.threshold:
                    return False
                    
        return True
                
            
