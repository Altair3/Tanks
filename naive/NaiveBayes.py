import sys
import math
from os import listdir




def removePunc(word):
    for c in word:
        if(c == ',' or c =='?' or c == '\'' or c == '\"' or c == '.' or c == '!' or c == ':' or c ==';'):
            word = word.replace(c,"")
    return word

def createBlankGroupsDict(groups):
    rval = {}
    
    for group in groups:
        rval[group] = 0
    
    return rval

def cleanWord(word):
    word = word.strip()
    word = removePunc(word)
    word = word.lower()    
    return word

def addWordMultinomial(word, words,fileWordCount):
    fileWordCount += 1
    
    if word not in words:
        words[word] = createBlankGroupsDict(groups)
    words[word][group] += 1
    
    return fileWordCount

def addWordBernoulli(word, words):
    if word not in words:
        words[word] = createBlankGroupsDict(groups)
    words[word][group] += 1
    
def maxDictionary(dict):
    curMax = -1000000
    curKey = None
    
    for k,v in dict.items():
        if v > curMax:
            curMax = v
            curKey = k
    
    return curKey
    

if __name__ == '__main__':
    newsgroups = [ f for f in listdir("train/")]
    
    mode = 'multinomial'
    
    numDocuments = {}
    totalDocumentCount = 0
    groups = []
    wordCount = {}
    words = {}
    
    confusionMatrix = {}
    
    for group in newsgroups:
        path = "train/" + group
        
        numDocuments[group] = len([name for name in listdir(path)])
        wordCount[group] = 0
        confusionMatrix[group] = {}
        groups.append(group)
    
    '''training'''    
    for group in newsgroups:
        path = "train/" + group + "/"
        
        for file in listdir(path):
            fileWordCount = 0
            wordsInFile = []
            
            filepath = path + file
            f = open(filepath, 'r')
            
            for line in f:
                lineWords = line.split()
                
                for word in lineWords:    
                    word = cleanWord(word)
                    if word.isspace() or word == None:
                        continue
                    
                    if mode == 'multinomial':
                        fileWordCount = addWordMultinomial(word, words,fileWordCount)
                    elif mode == 'bernoulli':
                        if word not in wordsInFile:
                            fileWordCount += 1
                            wordsInFile.append(word)
                            addWordBernoulli(word, words)
                    else:
                        pass
            wordCount[group] += fileWordCount
            #print("Finished reading file: " + file)
        print("Finished training: " + group + ", total documents: " + str(numDocuments[group]) + ", total word count: " + str(wordCount[group]))
        
    for k in numDocuments.keys():
        totalDocumentCount += numDocuments[k]
    
    '''testing'''
    print "begining testing"
    path = "test/"
    accuracy = 0
    total = 0
    for name in newsgroups:
        
        filepath = path + name + "/"
        specificAccuracy = 0
        specTotal = 0
        for d in listdir(filepath):
            d = filepath + d
            f = open(d, "r")
            
            currentProbability = createBlankGroupsDict(groups)
            
            #priors
            for group, probabilty in currentProbability.items():
                currentProbability[group] = math.log(float(numDocuments[group])/float(totalDocumentCount))
            
            for line in f:
                lineWords = line.split()
                
                for word in lineWords:    
                    word = cleanWord(word)
                    if word == None:
                        continue
                    
                    if word in words:
                        for g, count in words[word].items():
                            if count != 0:
                                currentProbability[g] *= math.log(float(count)/float(wordCount[g]))
                            
            prediction = maxDictionary(currentProbability)
        
            #add in a confused matrix
            if prediction not in confusionMatrix[name]:
                confusionMatrix[name][prediction] = 0
            confusionMatrix[name][prediction] += 1
            
            total+=1
            specTotal+=1
            if prediction == name:
                accuracy+=1
                specificAccuracy+=1
                
        print "finished ", name, ", current accuracy: ", str(float(accuracy)/float(total))
        print "specific accuracy", str(float(specificAccuracy)/float(specTotal))

    print "total accuracy" , float(accuracy)/float(total)
    
                    
        
        
    
    
        
        