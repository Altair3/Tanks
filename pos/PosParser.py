import sys
import random
import time
import math
from os import listdir

posList = ["#", "$", "CC", "''", ",", ".", ":", "``", "CD", "DT", "EX", "FW", "IN", "JJ", "JJR", "JJS", "LS", "MD", "NN", "NNP", "NNPS", "NNS", "PDT", "POS", "PRP", "PRP$", "RB", "RBR", "RBS", "RP", "SYM", "TO", "UH", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "WDT", "WP", "WP$", "WRB"]
SMALLNUMBER = 0
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
        used to calculate prior
        '''
        
        
    def leppard(self):
        pass
        
class PosParser(object):
    
    def __init__(self, contextLength):
        
        self.posMaps = {}
        self.contextLength = contextLength
        
        for p in posList:
            self.posMaps[p] = PartOfSpeech(p)
            
        self.totalBeginSentences = 0
        self.trainingwords = []
        
        '''
        map
        key: the context
        value: number of times the key began a sentence
        example: {["DT, NN"] = 4} means that a determiner (DT) followed by a noun (NN) began a sentence 4 times
        '''
        self.beginSentences = {}
        self.numBeginSentence = 0
        self.priors = {}
        
        '''
        map
        key: the context
        value: number of times the following POS was the key
        example: {["DT, NN"] = {NN: 4}} means that a determiner (DT) followed by a noun (NN) preceded a NN 4 times
        '''
        self.transitionMap = {}
        self.totalTransitions = {}
        
        self.transitionProbMap = {}
        
        
    def parseFile(self, fileName):
        
        f = open(fileName, 'r')
        data = f.read()
        data = data.split()
    
        prevPosNames = []
        
        for i in range(self.contextLength):
            prevPosNames.append(None)         
    
        for token in data:
            prevPosNamesString = ""
            if None not in prevPosNames:
                prevPosString = self.getContextString(prevPosNames, self.contextLength)
            
            word, posName = self.splitToken(token)
            self.trainingwords.append(word)
            if word in self.posMaps[posName].emissionMap:
                self.posMaps[posName].emissionMap[word] += 1
            else:
                self.posMaps[posName].emissionMap[word] = 1
            self.posMaps[posName].totalEmissions += 1
            
            if None not in prevPosNames:
                if prevPosNamesString not in self.transitionMap:
                    self.transitionMap[prevPosNamesString] = {}
            
                if posName in self.transitionMap[prevPosNamesString]:
                    self.transitionMap[prevPosNamesString][posName] += 1
                else:
                    self.transitionMap[prevPosNamesString][posName] = 1
                    
                if prevPosNamesString not in self.totalTransitions:
                    self.totalTransitions[prevPosNamesString] = 0
                self.totalTransitions[prevPosNamesString] += 1
            
            context = self.getContextString(prevPosNames, self.contextLength)
                    
            if context != "" and prevPosNames[0] == ".":
                if context not in self.beginSentences:
                    self.beginSentences[context] = 0
                self.beginSentences[context] += 1
            
            if self.contextLength == 1:
                prevPosNames[0] = posName
            else:
                prevPosNames[0] = prevPosNames[1]
                prevPosNames[1] = posName
                            
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
    
    '''
    contextList: a list of strings that are POSs
    contextLength: the length of the list
    '''
    def getContextString(self, contextList, contextLength):
        if None in contextList:
            return ""
        prevPosNamesString = ""
        for i in range(contextLength):
            prevPosNamesString += contextList[i]
            if i != (contextLength-1):
                prevPosNamesString += ", "
                
        return prevPosNamesString
    
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
        for k3, v3 in self.transitionMap:
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
        print self.transition_probability
    
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
            curObs = obs[t]
            if curObs not in self.trainingwords:
                print "curobs" , curObs
                V.append({})
                continue
            V.append({})
            newpath = {}
            
            for pos in posList:
                #(prob,state) = max((V[t-1][pos0] * self.transition_probability[pos0][pos] * self.emission_probability[pos][obs[t]],pos0) for pos0 in posList)
                
                if obs[t] not in self.emission_probability[pos]:
                    V[t][pos] = SMALLNUMBER
                    continue
                
                xlist = []

                for pos0 in posList:
                    
                    if pos0 not in V[t-1]:
                        pass
                        #print "x"
                    if pos not in self.transition_probability[pos0]:
                        pass
                        #print "y"
                    
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
    trash,parseFlag,ngramFile, contextLength = sys.argv
    if(parseFlag == "t"):
        parser = PosParser(int(contextLength))
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
        
        prob,path = parser.Viterbi(observation)
        print "prob" , prob
        print "path" , path

    
    #ngram = NGram()
    #ngram.doIt("ngram/" + ngramFile)
    #print(ngram.sentence)
