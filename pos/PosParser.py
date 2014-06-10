import sys
import random
import time
import math


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
        used to calculate prior
        '''
        self.numBeginSentence = 0
        self.prior = None
        
        
    def leppard(self):
        pass
        
class PosParser(object):
    
    def __init__(self,order):
        self.order = order
        self.posMaps = {}
        self.posList2 = []
        if(self.order == 2):
            #create a combination list
            for p in posList:
                for p2 in posList:
                    pair = str(p + ", " + p2)
                    self.posList2.append(pair)
        if(self.order == 1):
            self.posList2 = posList
                
        for p in posList:
            self.posMaps[p] = PartOfSpeech(p)
        
         
        '''
        map
        key: the part of speech
        value: number of times the following POS was the key
        example: {[DT]=4} means that a determiner (DT) followed this POS 4 times
        '''
        self.transitionMap = {}
        self.totalTransitions = {}
        self.transitionProbMap = {}
        for pos in self.posList2:
            self.transitionMap[pos] = {}
            self.totalTransitions[pos] = 0
            self.transitionProbMap[pos] = {}
        
        
        
             
        self.totalBeginSentences = 0
        self.trainingwords = []
        
    def parseFile(self, fileName):
        
        f = open(fileName, 'r')
        data = f.read()
        data = data.split()
        posName = ""
        if(self.order == 1):
            prevPosName = None
        else:
            prevPosName = ["",""]
        for token in data:
            word, posName = self.splitToken(token)
            self.trainingwords.append(word)
            if word in self.posMaps[posName].emissionMap:
                self.posMaps[posName].emissionMap[word] += 1
            else:
                self.posMaps[posName].emissionMap[word] = 1
            self.posMaps[posName].totalEmissions += 1
            
            if(self.order == 1):
                                               
                if prevPosName != None:
                    if posName not in self.transitionMap[prevPosName]:
                        self.transitionMap[prevPosName][posName] = 0
                    self.transitionMap[prevPosName][posName] += 1
                    self.totalTransitions[posName] += 1
                
                if (prevPosName == None) or (prevPosName == "."):
                    self.posMaps[posName].numBeginSentence += 1
                    self.totalBeginSentences += 1
                
                prevPosName = posName  
                       
            else:

                if prevPosName[1] == "":
                    prevPosName[1] = posName
                    self.posMaps[posName].numBeginSentence += 1
                    self.totalBeginSentences += 1
                    continue
                elif(prevPosName[0] == "" and prevPosName[1] != ""):
                    prevPosName[0] = prevPosName[1]
                    prevPosName[1] = posName
                else:
                    key = str(prevPosName[0] + ", " + prevPosName[1])
                    if posName not in self.transitionMap[key]:
                        self.transitionMap[key][posName] = 0
                    self.transitionMap[key][posName] += 1
                    self.totalTransitions[key] += 1
                    if(prevPosName[1] == "."):
                        self.posMaps[posName].numBeginSentence += 1
                        self.totalBeginSentences += 1
                    prevPosName[0] = prevPosName[1]
                    prevPosName[1] = posName                      
                               
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
                    
            if self.totalTransitions == 0:
                continue
            for context, contextMap in self.transitionMap.items():
                for posName, value in contextMap.items():
                    if(self.totalTransitions[context] == 0 or (float(value)/float(self.totalTransitions[context]) == 0)):
                        self.transitionProbMap[context][posName] = SMALLNUMBER
                    else:
                       
                        self.transitionProbMap[context][posName] = math.log((float(value)/float(self.totalTransitions[context]))+1)
                        
    def train(self, rootFolder):
        
        print("Beginning training")
        startTime = time.time()
        
        self.parseFile(rootFolder + "allTraining.txt")
         
        self.CalculatePriors()
        self.CalculateProbabilities()
        
        self.start_probability = {}
        self.transition_probability = {}
        
        listOfRemovedCrap = []
        for context in self.posList2:
            
            if self.transitionProbMap[context]:
                self.transition_probability[context] = self.transitionProbMap[context]
            else:
                listOfRemovedCrap.append(context)
        for i in listOfRemovedCrap:
            self.posList2.remove(i)
            
        print "After removal:", len(self.posList2)
        
        self.emission_probability = {}
        for k,v in self.posMaps.items():
            self.start_probability[k] = v.prior
            
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
                                 
                xlist = []

                if obs[t] not in self.emission_probability[pos]:
                    term3 = SMALLNUMBER                                
                else:                          
                    term3 = self.emission_probability[pos][obs[t]]
                if(self.order == 2):
                                 
                    for pos0 in self.posList2:
                        
                        if pos not in self.transition_probability[pos0]:
                            
                            term2 = SMALLNUMBER
                        else:
                            term2 = self.transition_probability[pos0][pos] 
                                                                             
                        for pos2 in posList:
                            term1 = V[t-1][pos2]                                           
                            total = term1 + term2 + term3                          
                            xlist.append((total,pos2))
                        
                else:   
                    for pos0 in self.posList2: 
                        term1 = V[t-1][pos0]  
                        
                        if pos not in self.transition_probability[pos0]:
                            term2 = SMALLNUMBER
                        else:
                            term2 = self.transition_probability[pos0][pos]  
                                             
                        if obs[t] not in self.emission_probability[pos]:
                            total = term1 + term2 + SMALLNUMBER
                            
                        else:                          
                            term3 = self.emission_probability[pos][obs[t]]                   
                            total = term1 + term2 + term3
                        
                        xlist.append((total,pos0))
                                    
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
        
        self.contextconst = ["",""]
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
        


def printConfusionMatrix(confusionMatrix):
    builder = ""
    for pos,row in sorted(confusionMatrix.items()):
        for key,value in sorted(row.items()):
            if value > 4 and key != pos:
                builder += pos + "confused with " + key + " " + str(value) + "times\n" 
    print "\n\n\n", builder

if __name__ == '__main__':
    trash,parseFlag,ngramFile,order = sys.argv
    if(parseFlag == "t"):
        parser = PosParser(int(order))
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
        confusionMatrix = {}
        for i in posList:
            confusionMatrix[i] = {}
            for j in posList:
                confusionMatrix[i][j] = 0
        confusionMatrix["-LRB-"] = {}
        confusionMatrix["-RRB-"] = {}
        for j in posList:
            confusionMatrix["-LRB-"][j] = 0
            confusionMatrix["-RRB-"][j] = 0     
        for i in range(len(labels)):
            confusionMatrix[labels[i]][path[i]] += 1
            if labels[i] == path[i]: 
                accuracy += 1
     
        print "accuracy" , str(float(accuracy)/len(labels))
        printConfusionMatrix(confusionMatrix)
        print "prob" , prob
    else:
        n = NGram()
        n.doIt(ngramFile)
        print n.sentence
