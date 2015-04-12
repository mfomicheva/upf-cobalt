from aligner import *
from util import *
from scorer import *
import codecs
import getopt
import sys
from os import listdir
from os.path import isfile, join
from os.path import expanduser


refDir = '/Users/MarinaFomicheva/Dropbox/workspace/dataSets/wmt2007-data/es-en_judged/parsed/references'
testDir = '/Users/MarinaFomicheva/Dropbox/workspace/dataSets/wmt2007-data/es-en_judged/parsed/system-outputs'
outputDir = '/Users/MarinaFomicheva/Dropbox/workspace/alignment/results/wmt2007/mwa/systran_tmp'
dataset = 'nc-test2007'

referenceFiles = [f for f in listdir(refDir + '/' + dataset) if isfile(join(refDir + '/' + dataset, f))]
testFiles = [f for f in listdir(testDir + '/' + dataset) if isfile(join(testDir + '/' + dataset, f))]

for r in referenceFiles:

    sentencesRef = readSentences(codecs.open(refDir + '/' + dataset + '/' + r, encoding = 'UTF-8'))

    for t in testFiles:

        if 'systran' not in t:
            continue

        sentencesTest = readSentences(codecs.open(testDir + '/' + dataset + '/' + t, encoding = 'UTF-8'))
        outputFileScoring = open(outputDir + '/' + t +'.scoring.out', 'w')
        outputFileAlign = open(outputDir + '/' + t + '.align.out', 'w')

        scorer = Scorer()
        aligner = Aligner('english')

        for i, sentence in enumerate(sentencesRef):
            alignments = aligner.align(sentencesTest[i], sentence)
            score = scorer.calculateScore(sentencesTest[i], sentence, alignments)

            outputFileScoring.write(str(score) + '\n')
            for index in xrange(len(alignments[0])):
                outputFileAlign.write(str(alignments[0][index]) + " : " + str(alignments[1][index]) + " : " + str(alignments[2][index])+'\n')

        outputFileScoring.close()
        outputFileAlign.close()
