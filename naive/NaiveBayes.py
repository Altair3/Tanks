import sys
import math
from os import listdir




def removePunc(word):
    for c in word:
        if(c == '(' or c == ')' or c == '@' or c == ',' or c =='?' or c == '\'' or c == '\"' or c == '.' or c == '!' or c == ':' or c ==';'):
            word = word.replace(c,"")
    return word

def createBlankGroupsDict(groups):
    rval = {}
    
    for group in groups:
        rval[group] = 0
    
    return rval
    
def cleanWord(word):
    word = word.strip()
    #word = removePunc(word)
    if word.isdigit():
        return None
    word = word.lower() 
    if len(word) == 0:
        return None  
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
    count = 0
    for k,v in dict.items():
        if count == 0:
            curMax = v
            curKey = k
        else:
            if v > curMax:
                curMax = v
                curKey = k
        count += 1
    
    return curKey
    
def printConfusionMatrix(confusionMatrix):
    builder = ""
    justvalues = ""
    for newsgroup,row in sorted(confusionMatrix.items()):
        for key,value in sorted(row.items()):
            builder += "      " + str(key).rjust(5) + " "
        builder += "\n" + newsgroup
        for key,value in sorted(row.items()):
            builder += " " + str(value).rjust(5) + " "
            justvalues += " " + str(value).rjust(5) + " "
        builder += "\n"
        justvalues +="\n"
    print builder
    print "\n\n\n", justvalues

if __name__ == '__main__':
    newsgroups = [ f for f in listdir("train/")]
    
    mode = 'bernoulli'
    
    numDocuments = {}
    totalDocumentCount = 0
    groups = []
    wordCount = {}
    words = {}
    

    confusionMatrix = {}

    stopwords = []
    
    f = open("stopwords_en.txt", "r")
    for stopword in f:
        stopword = stopword.strip()
        stopwords.append(stopword)
    f.close()
    
    
    for group in newsgroups:
        path = "train/" + group
      
        numDocuments[group] = len([name for name in listdir(path)])
        wordCount[group] = 0
        confusionMatrix[group] = {}
        for group2 in newsgroups:
            confusionMatrix[group][group2] = 0
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
                    if word == None or word.isspace() or word in stopwords:
    
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
                currentProbability[group] = (float(numDocuments[group])/float(totalDocumentCount))
            
            for line in f:
                lineWords = line.split()
                
                for word in lineWords:    
                    word = cleanWord(word)
                    if word == None or word in stopwords:
                        continue
                    
                    if word in words:
                        '''this is our issue area'''
                        for g, count in words[word].items():
                            if True:
                                if mode == 'multinomial':
                                    currentProbability[g] *= (float(count+1)/float(wordCount[g]))
                                else:
                                    currentProbability[g] *= (float(count+1)/float(numDocuments[g]))                         
                            
            prediction = maxDictionary(currentProbability)
            
            confusionMatrix[name][prediction] += 1
            
            total+=1
            specTotal+=1
            if prediction == name:
                accuracy+=1
                specificAccuracy+=1
                
        print "finished ", name, ", current accuracy: ", str(float(accuracy)/float(total))
        print "specific accuracy", str(float(specificAccuracy)/float(specTotal))

    print "total accuracy" , float(accuracy)/float(total)
    
    printConfusionMatrix(confusionMatrix)
    
    
