import sys
import math
from os import listdir

def createBlankGroupsDict(groups):
    rval = {}
    
    for group in groups:
        rval[group] = 0
    
    return rval

def cleanWord(word):
    word = word.strip()
    word = word.lower()
    return word

def addWordMultinomial(word, words, group,fileWordCount):
    fileWordCount += 1
    
    if word not in words:
        words[word] = createBlankGroupsDict(groups)
    words[word][group] += 1
    
    return fileWordCount

def addWordBernoulli(word, words,group):
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
    
    mode = 'categorical'
    
    numDocuments = {}
    totalDocumentCount = 0
    groups = []
    wordCount = {}
    words = {}
    
    
    for group in newsgroups:
        path = "train/" + group
        
        numDocuments[group] = len([name for name in listdir(path)])
        wordCount[group] = 0
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
                    if word.isspace():
                        continue
                    
                    if mode == 'categorical':
                        fileWordCount = addWordMultinomial(word, words,group, fileWordCount)
                    elif mode == 'multivariate':
                        if word not in wordsInFile:
                            fileWordCount += 1
                            wordsInFile.append(word)
                            addWordBernoulli(word, words,group)
                    else:
                        pass
            wordCount[group] += fileWordCount
            #print("Finished reading file: " + file)
        print("Finished training: " + group + ", total documents: " + str(numDocuments[group]) + ", total word count: " + str(wordCount[group]))
        
    for k in numDocuments.keys():
        totalDocumentCount += numDocuments[k]
    
    '''testing'''
    path = "test/"
    
    filepath = path + "talk.politics.misc/178474"
    f = open(filepath, "r")
    
    currentProbability = createBlankGroupsDict(groups)
    
    #priors
    for group, probabilty in currentProbability.items():
        currentProbability[group] = math.log(float(numDocuments[group])/float(totalDocumentCount))
    
    for line in f:
        lineWords = line.split()
        
        for word in lineWords:    
            word = cleanWord(word)
            
            if word in words:
                for group, count in words[word].items():
                    if count != 0:
                        currentProbability[group] *= math.log(float(count)/float(wordCount[group]))
                    
    print(currentProbability)
    
    print(maxDictionary(currentProbability))
                    
                    
        
        
    
    
        
        
