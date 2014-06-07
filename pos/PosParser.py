import sys
import random
import time
from os import listdir

posList = ["#", "$", "``", "''", "(", ")", ",", "--", ".", ":", "CC", "CD", "DT", "EX", "FW", "IN", "JJ", "JJR", "JJS", "LS", "MD", "NN", "NNP", "NNPS", "NNS", "PDT", "POS", "PRP", "PRP$", "RB", "RBR", "RBS", "RP", "SYM", "TO", "UH", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "WDT", "WP", "WP$", "WRB"]

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
        
        '''
        used to calculate prior
        '''
        self.numBeginSentence = 0
        self.prior = None
        
        
    def leppard(self):
        pass
        
class PosParser(object):
    
    def __init__(self):
        
        self.posMaps = {}
        
        for p in posList:
            self.posMaps[p] = PartOfSpeech(p)
            
        self.totalBeginSentences = 0
            
    def parseFile(self, fileName):
        
        f = open(fileName, 'r')
        data = f.read()
        data = data.split()
    
        posName = ""
        prevPosName = None
    
        for token in data:
            word, posName = self.splitToken(token)
            if word in self.posMaps[posName].emissionMap:
                self.posMaps[posName].emissionMap[word] += 1
            else:
                self.posMaps[posName].emissionMap[word] = 1
            self.posMaps[posName].totalEmissions += 1
                
            if prevPosName != None:
                if posName in self.posMaps[prevPosName].transitionMap:
                    self.posMaps[prevPosName].transitionMap[posName] += 1
                else:
                    self.posMaps[prevPosName].transitionMap[posName] = 1
                self.posMaps[prevPosName].totalTransitions += 1
            
            if (prevPosName == None) or (prevPosName == "."):
                self.posMaps[posName].numBeginSentence += 1
                self.totalBeginSentences += 1
            
            prevPosName = posName            
                            
        f.close()
    
    '''
    Splits the token into word and part of speech name
    token: the string in the format of [word]_[posName]
    '''
    def splitToken(self, token):
        underscoreIndex = token.index('_')
        word = token[:underscoreIndex]
        posName = token[underscoreIndex+1:]
        
        return word, posName
    
    def CalculatePriors(self):
        for k,v in self.posMaps.items():
            v.prior = (float(v.numBeginSentence)/float(self.totalBeginSentences))
            
    def CalculateProbabilities(self):
        for k1,v1 in self.posMaps.items():
            for k2,v2 in v1.emissionMap.items():
                v1.emissionProbMap[k2] = (float(v2)/float(v1.totalEmissions))
            for k3,v3 in v1.transitionMap.items():
                v1.transitionProbMap[k3] = (float(v3)/float(v1.totalTransitions))
    
    '''
    rootFolder: the folder containing the folders with the .mrg files
    in this project, rootFolder is "../assignment3"
    '''
    def ParseItAll(self, rootFolder):
        
        print("Beginning training")
        startTime = time.time()
        
        '''
        folders = [ f for f in listdir(rootFolder)]
        numFolders = len(folders)
        
        trainCount = 0
        
        for folder in folders:
            path = rootFolder + folder + "/"
            
            for file in listdir(path):
                fileName = path + file
                
                self.parseFile(fileName)
                
            trainCount += 1
            print("Finished training:", folder, "(", str(trainCount), "/", str(numFolders), ")")
        '''
        
        self.parseFile(rootFolder + "allTraining.txt")
         
        self.CalculatePriors()
        self.CalculateProbabilities()
            
        endTime = time.time()
            
        print "Finished training. Total time:", str(endTime-startTime), "seconds"
        
class NGram(object):
    def __init__(self):
        self.contextconst = [""]
        self.sentence = ""
        
    def doIt(self, fileName):
        
        infilename = fileName
        trainingdata = open(infilename).read()
         
        context = self.contextconst
        model = {}
         
        for word in trainingdata.split():
            model[str(context)] = model.setdefault(str(context),[])+ [word]
            context = (context+[word])[1:]
         
        context = self.contextconst
        for i in range(100):
            word = random.choice(model[str(context)])
            context = (context+[word])[1:]
            self.sentence += word + " "
        
if __name__ == '__main__':
    
    parser = PosParser()
    parser.ParseItAll("assignment3/")
    
    ngram = NGram()
    ngram.doIt("ngram/revelation13")
    print(ngram.sentence)
