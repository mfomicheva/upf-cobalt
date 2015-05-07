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


def loadVectors(fileName = '/Users/MarinaFomicheva/workspace/resources/distribSim/vectors_dep'):

    vectorFile = open (fileName, 'r')

    for line in vectorFile:
        if line == '\n':
        # here line = {str} 'version https://git-lfs.github.com/spec/v1\n'
        # next line = 'oid sha256:e256c308eb8510d98240926363be4e5d80dd0a343f53877c83e1243a5bf52cac'
        # next line = 'size 860005638'

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




