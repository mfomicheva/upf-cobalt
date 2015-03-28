from aligner import *
from util import *
from scorer import *
import codecs
import os

dir2process = 'Data/wmt2007-data/es-en_judged/parsed'
outputDir = 'Output/wmt2007/mwa/tmp3'
referenceFiles = readFileNames(open('Data/wmt2007-data/filesListReferences.txt'))
testFiles = readFileNames(open('Data/wmt2007-data/filesListTest.txt'))

scorer = Scorer()
aligner = Aligner('english')

if not os.path.exists(outputDir):
    os.makedirs(outputDir)

for r in referenceFiles:

    if 'nc' in r:
        dataSet = 'nc-test'
        outputFileNameRef = 'news_'
    else:
        dataSet = 'test'
        outputFileNameRef = 'europarl_'

    sentencesRef = readSentences(codecs.open(dir2process+'/'+r, encoding='UTF-8'))
    for t in testFiles:
        if (dataSet == 'nc-test' and 'nc' not in t) or (dataSet == 'test' and 'nc' in t):
            continue
        outputFileNameTest=t
        outputFileScoring = open(outputDir + '/' + outputFileNameRef + outputFileNameTest + '.scoring.out', 'w')
        outputFileAlign = open(outputDir + '/' + outputFileNameRef + outputFileNameTest + '.align.out', 'w')
        sentencesTest = readSentences(codecs.open(dir2process + '/' + t, encoding='UTF-8'))
        for i, sentence in enumerate(sentencesRef):
            alignments = aligner.align(sentencesTest[i], sentence)
            score = scorer.calculateScore(sentencesTest[i], sentence, alignments)

            outputFileScoring.write(str(score) + '\n')
            for index in xrange(len(alignments[0])):
                outputFileAlign.write(str(alignments[0][index]) + " : " + str(alignments[1][index]) + " : " + str(alignments[2][index])+'\n')

        outputFileScoring.close()
        outputFileAlign.close()
