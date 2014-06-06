import sys

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
        totalEmissions = 0
        
        self.emissionProbMap = {}
        
        '''
        map
        key: the part of speech
        value: number of times the following POS was the key
        exampe: {[DT]=4} means that a determiner (DT) followed this POS 4 times
        '''
        self.transitionMap = {}
        totalTransitions = 0
        
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
            token = self.cleanToken(token)
            #the previous token was a POS tag
            if posState == True:
                if token in self.posMaps[posName].emissionMap:
                    self.posMaps[posName].emissionMap[token] += 1
                else:
                    self.posMaps[posName].emissionMap[token] = 1
                posState = False
                prevPosName = posName
            #the previous token was not a POS tag
            else:
                if token in posList:
                    posState = False
                    posName = token
                    
                    if prevPosName != "":
                        if posName in self.posMaps[prevPosName].transitionMap:
                            self.posMaps[prevPosName].transitionMap[posName] += 1
                        else:
                            self.posMaps[prevPosName].transitionMap[posName] = 1
                
    def cleanToken(self, token):
        if token[0] == "(":
            token = token[1:]
        if token[-1] == ")":
            token = token[:-1]
            
        return token
        
if __name__ == '__main__':
    
    parser = PosParser()
    
    parser.parseFile("wsj_0201.mrg")
    
    f.close()
        
        
