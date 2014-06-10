import sys
import random
import time
import math
from os import listdir
from token import STAR

posList = ["#", "$", "''", ",", ".", ":", "``", "CC", "CD", "DT", "EX", "FW", "IN", "JJ", "JJR", "JJS", "LS", "MD", "NN", "NNP", "NNPS", "NNS", "PDT", "POS", "PRP", "PRP$", "RB", "RBR", "RBS", "RP", "SYM", "TO", "UH", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "WDT", "WP", "WP$", "WRB"]
SMALLNUMBER = -1
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
        example: {[DT]=4} means that a determiner (DT) followed this POS 4 times
        '''
        self.transitionMap = {}
        for pos in posList:
            self.transitionMap[pos] = 0
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
        self.trainingwords = []
    def parseFile(self, fileName):
        
        f = open(fileName, 'r')
        data = f.read()
        data = data.split()
    
        posName = ""
        prevPosName = None
    
        for token in data:
            word, posName = self.splitToken(token)
            self.trainingwords.append(word)
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
            if((float(v.numBeginSentence)/float(self.totalBeginSentences)) == 0):
                v.prior = SMALLNUMBER
            else:
                v.prior = math.log((float(v.numBeginSentence)/float(self.totalBeginSentences))+1)
            
    def CalculateProbabilities(self):
        for k1,v1 in self.posMaps.items():
            for k2,v2 in v1.emissionMap.items():
                if((float(v2)/float(v1.totalEmissions) ==0)):
                    v1.emissionProbMap[k2] = SMALLNUMBER
                else:
                    v1.emissionProbMap[k2] = math.log((float(v2)/float(v1.totalEmissions))+1)
            if v1.totalTransitions == 0:
                continue
            for k3,v3 in v1.transitionMap.items():
                if((float(v3)/float(v1.totalTransitions) == 0)):
                    v1.transitionProbMap[k3] = SMALLNUMBER
                else:
                    v1.transitionProbMap[k3] = math.log((float(v3)/float(v1.totalTransitions))+1)
    
    '''
    rootFolder: the folder containing the folders with the .mrg files
    in this project, rootFolder is "../assignment3"
    '''
    def train(self, rootFolder):
        
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
        
        self.start_probability = {}
        self.transition_probability = {}
        self.emission_probability = {}
        for k,v in self.posMaps.items():
            self.start_probability[k] = v.prior
            self.transition_probability[k] = v.transitionProbMap
            self.emission_probability[k] = v.emissionProbMap
        
                  
            
        endTime = time.time()
            
        print "Finished training. Total time:", str(endTime-startTime), "seconds"
    
    def Viterbi(self,obs):
        V = [{}]
        path = {}
        
        for pos in posList:
            if(obs[0] in self.emission_probability[pos]):
                V[0][pos] = self.start_probability[pos] + self.emission_probability[pos][obs[0]]
                path[pos] = [pos]
            else:
                V[0][pos] = SMALLNUMBER
                path[pos] = [pos]
        
        for t in range(1,len(obs)):            
            V.append({})
            newpath = {}
            for pos in posList:
                #(prob,state) = max((V[t-1][pos0] * self.transition_probability[pos0][pos] * self.emission_probability[pos][obs[t]],pos0) for pos0 in posList)                      
                xlist = []

                for pos0 in posList:
                    
                    if pos0 not in V[t-1]:
                        pass
                        #print "x"
                    if pos not in self.transition_probability[pos0]:
                        pass
                        #print "y"
                    if obs[t] not in self.emission_probability[pos]:
                        term1 = V[t-1][pos0]
                        term2 = self.transition_probability[pos0][pos]
                        total = term1 + term2 + SMALLNUMBER
                        
                    else:
                        term1 = V[t-1][pos0]
                        term2 = self.transition_probability[pos0][pos]
                        term3 = self.emission_probability[pos][obs[t]]                   
                        total = term1 + term2 + term3
                    
                    xlist.append((total,pos0))
                    #xlist.append((V[t-1][pos0] * self.transition_probability[pos0][pos] * self.emission_probability[pos][obs[t]],pos0))
                
                (prob, state) = max(xlist)
          
                V[t][pos] = prob
                if state not in path:
                    #pass
                    
                    #print "p"
                    continue
                newpath[pos] = path[state] + [pos]
          
            path = newpath
            
        n = 0
        if len(obs)!=1:
            n = t
        map = V[n]
        (prob,state) = max((V[n][pos],pos) for pos in posList)
        return (prob,path[state])
         
        
       
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
    trash,parseFlag,ngramFile = sys.argv
    if(parseFlag == "t"):
        parser = PosParser()
        parser.train("assignment3/")
        f = open("assignment3/devtest.txt","r")
        data = f.read()
        data = data.split()
        observation = []
        labels = []
        for token in data:
            word,pos = parser.splitToken(token)
            observation.append(word)
            labels.append(pos)
        starttime = time.time()
        prob,path = parser.Viterbi(observation)
        end = time.time()
        print end-starttime
        accuracy = 0
        for i in range(len(labels)):
            if labels[i] == path[i]:
                accuracy += 1
        
        print "accuracy" , str(float(accuracy)/len(labels))
        print "prob" , prob
        
