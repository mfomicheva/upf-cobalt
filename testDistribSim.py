__author__ = 'MarinaFomicheva'

import re
import math
from types import *
from nltk.corpus import wordnet

def distributionalSimilarity(word1, word2):

    vectorSimilarity = 0

    if word1.lower() in wordVector and word2.lower() in wordVector:
        vector1 = wordVector[word1.lower()].split( )
        vector2 = wordVector[word2.lower()].split( )
        sumxx, sumxy, sumyy = 0, 0, 0

        for i in range(len(vector1)):
            x = float(vector1[i])
            y = float(vector2[i])
            sumxx += x * x
            sumyy += y * y
            sumxy += x * y
        vectorSimilarity = sumxy/math.sqrt(sumxx * sumyy)
    return vectorSimilarity


def loadVectors(fileName = '/home/u88591/Workspace/distributional-similarity/deps.words'):

    vectorFile = open (fileName, 'r')

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
loadVectors()

word1 = "dog"
word2 = "animal"
vectorSim = distributionalSimilarity(word1, word2)
print "Distributional Similarity = " + str(vectorSim)




