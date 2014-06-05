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
        
        self.PosMaps = {}
        
        for p in posList:
            self.PosMaps[p] = PartOfSpeech(p)
        
if __name__ == '__main__':
    
    parser = PosParser()
    
    f = open("wsj_0201.mrg", 'r')
    
    data = f.read()
    
    data = data.split()
    
    for token in data:
        
    
    f.close()
        
        
