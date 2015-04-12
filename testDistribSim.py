__author__ = 'MarinaFomicheva'

import re
import math
from types import *
from nltk.corpus import wordnet

def wordnetSimilarity(word1, word2):

    synsets1 = wordnet.synsets(word1)
    synsets2 = wordnet.synsets(word2)

    max_similarity = 0

    for synset1 in synsets1:
        for synset2 in synsets2:
            if synset1._pos == synset2._pos:
                similarity = wordnet.path_similarity(synset1, synset2)
            else:
                similarity = 0
            if max_similarity < similarity:
                max_similarity = similarity

    return max_similarity

def distributionalSimilarity(word1,word2):

    vectorSimilarity = 0

    if word1.lower() in wordVector and word2.lower() in wordVector:
        vector1 = wordVector[word1.lower()].split( )
        vector2 = wordVector[word2.lower()].split( )
        sumxx, sumxy, sumyy = 0, 0, 0

        for i in range(len(vector1)):
            x = float(vector1[i])
            y = float(vector2[i])
            sumxx += x*x
            sumyy += y*y
            sumxy += x*y
        vectorSimilarity = sumxy/math.sqrt(sumxx*sumyy)
    return vectorSimilarity


def loadWordVectors(vectorsFileName = 'Resources/vectors/deps.words'):

    vectorFile = open (vectorsFileName, 'r')

    for line in vectorFile:
        if line == '\n':
            continue

        match = re.match(r'^([^ ]+) (.+)',line)
        if type(match) is NoneType:
            continue

        word = match.group(1)
        vector = match.group(2)

        wordVector[word] = vector

wordVector = {}
loadWordVectors()

testFile = open('Data/wordSimTest.txt','r')
for line in testFile:
    data = line.split("\t")
    word1 = data[0].lower()
    word2 = data[1].lower()
    source = data[2].strip()
    vectorSim = distributionalSimilarity(word1,word2)
    wnSim = wordnetSimilarity(word1,word2)
    print word1 + " - " + word2 + "\t" + str(vectorSim) + "\t" + str(wnSim) + "\t" + source



# word1 = "absence"
# word2 = "without"
# vectorSim = distributionalSimilarity(word1,word2)
# wnSim = wordnetSimilarity(word1,word2)
# print "Distributional Similarity = " + str(vectorSim)
# print "WordNet Path Similarity = " + str(wnSim)

