import sys
import time
from os import listdir

posList = ["$", "``", "\"", "(", ")", ",", "--", ".", ":", "CC", "CD", "DT", "EX", "FW", "IN", "JJ", "JJR", "JJS", "LS", "MD", "NN", "NNP", "NNPS", "NNS", "PDT", "POS", "PRP", "PRP$", "RB", "SYM", "TO", "UH", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "WDT", "WP", "WP$", "WRB"]

class PartOfSpeech(object):
    
    def __init__(self, name):
        
        self.name = name
        
        '''
        map
        key: the word
        value: number of times the key has appeared for this POS
        example: {[dog]=4} means that dog has appeared 4 times for this POS
        '''
        self.emissionMap = {}
        self.totalEmissions = 0
        
        self.emissionProbMap = {}
        
        '''
        map
        key: the part of speech
        value: number of times the following POS was the key
        exampe: {[DT]=4} means that a determiner (DT) followed this POS 4 times
        '''
        self.transitionMap = {}
        self.totalTransitions = 0
        
        self.transitionProbMap = {}
        
    def leppard(self):
        pass
        
class PosParser(object):
    
    def __init__(self):
        
        self.posMaps = {}
        
        for p in posList:
            self.posMaps[p] = PartOfSpeech(p)
            
    def parseFile(self, fileName):
        
        f = open(fileName, 'r')
        data = f.read()
        data = data.split()
    
        posState = False
        posName = ""
        prevPosName = ""
    
        for token in data:
            token = self.cleanToken(token, posState)
            #the previous token was a POS tag
            if posState == True:
                if token in self.posMaps[posName].emissionMap:
                    self.posMaps[posName].emissionMap[token] += 1
                else:
                    self.posMaps[posName].emissionMap[token] = 1
                self.posMaps[posName].totalEmissions += 1
                posState = False
                prevPosName = posName
            #the previous token was not a POS tag
            else:
                if token in posList:
                    posState = True
                    posName = token
                    
                    if prevPosName != "":
                        if posName in self.posMaps[prevPosName].transitionMap:
                            self.posMaps[prevPosName].transitionMap[posName] += 1
                        else:
                            self.posMaps[prevPosName].transitionMap[posName] = 1
                        self.posMaps[prevPosName].totalTransitions += 1    
                            
        f.close()
    
    '''
    Cleans the token of extra parentheses.
    token: string, the word or tag being cleaned
    posState: boolean, True = the previous token was a valid tag, False = otherwise
    '''
    def cleanToken(self, token, posState):
        if len(token) == 0:
            return ""
        
        if token[0] == "(":
            token = token[1:]
        
        if len(token) == 0:
            return ""
            
        if token[len(token)-1] == ")":
            token = token[:-1]
            
        if token == ")" and posState == False:
            token = ""
        
        return token
    
    '''
    rootFolder: the folder containing the folders with the .mrg files
    in this project, rootFolder is "../assignment3"
    '''
    def ParseItAll(self, rootFolder):
        
        folders = [ f for f in listdir(rootFolder)]
        numFolders = len(folders)
        
        startTime = time.time()
        
        trainCount = 0
        
        for folder in folders:
            path = rootFolder + folder + "/"
            
            for file in listdir(path):
                fileName = path + file
                
                parser.parseFile(fileName)
                
            trainCount += 1
            print("Finished training:", folder, "(", str(trainCount), "/", str(numFolders), ")")
            
        endTime = time.time()
            
        print("Finished training. Total time:", str(endTime-startTime), "seconds") 
        
if __name__ == '__main__':
    
    parser = PosParser()
    
    parser.ParseItAll("../assignment3/")
    
    #parser.parseFile("wsj_0201.mrg")
        
