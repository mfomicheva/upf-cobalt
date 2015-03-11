from aligner import *
from util import *
from scorer import *
import codecs
import re

#sentences = readSentences(open('Data/systran.es-en.test.primary.txt.out'))
#sentences = readSentences(open('/Users/MarinaFomicheva/Dropbox/workspace/dataSets/wmt2007-data/es-en_judged/parsed/systran.es-en.test.primary.txt.out'))
#sentences2 = readSentences(open('/Users/MarinaFomicheva/Dropbox/workspace/dataSets/wmt2007-data/es-en_judged/parsed/test2007.en.out'))

dir2process = '/Users/MarinaFomicheva/Dropbox/workspace/dataSets/wmt2007-data/es-en_judged/parsed'
outputDir = '/Users/MarinaFomicheva/Dropbox/workspace/alignment/results/wmt2007/mwa/systran_no_weighting_on_num_of_dependents'
referenceFiles = readFileNames(open('Data/filesListReferences.txt'))
testFiles = readFileNames(open('Data/filesListTest.txt'))


for r in referenceFiles:

    if 'nc' in r:
        dataSet = 'nc-test'
        outputFileNameRef = 'news_'
    else:
        dataSet = 'test'
        outputFileNameRef = 'europarl_'

    sentencesRef = readSentences(codecs.open(dir2process+'/'+r, encoding = 'UTF-8'))
    for t in testFiles:
        if (dataSet == 'nc-test' and 'nc' not in t) or (dataSet == 'test' and 'nc' in t):
            continue
        outputFileNameTest=t
        outputFileScoring = open(outputDir + '/' + outputFileNameRef + outputFileNameTest +'.scoring.out', 'w')
        outputFileAlign = open(outputDir + '/' + outputFileNameRef + outputFileNameTest +'.align.out', 'w')
        sentencesTest = readSentences(codecs.open(dir2process+'/'+t, encoding = 'UTF-8'))
        aligner = Aligner('english')
        scorer = Scorer()
        for i, sentence in enumerate(sentencesRef):
            alignments = aligner.align(sentencesTest[i], sentence)
            score = scorer.calculateScore(sentencesTest[i], sentence, alignments)

            outputFileScoring.write(str(score) + '\n')
            for index in xrange(len(alignments[0])):
                outputFileAlign.write(str(alignments[0][index]) + " : " + str(alignments[1][index]) + " : " + str(alignments[2][index])+'\n')

        outputFileScoring.close()
        outputFileAlign.close()




# sentencesRef = readSentences(codecs.open('Data/input-en-1.txt', encoding = 'UTF-8'))
# sentencesTest = readSentences(codecs.open('Data/input-en-2.txt', encoding = 'UTF-8'))
#
# aligner = Aligner('english')
# scorer = Scorer()
#
# for i, sentence in enumerate(sentencesRef):
#     alignments = aligner.align(sentencesTest[i], sentence)
#
#     ## print alignment and context information
#
#     for index in xrange(len(alignments[0])):
#           print str(alignments[0][index]) + " : " + str(alignments[1][index]) + " : " + str(alignments[2][index])
#
#     print scorer.calculateScore(sentencesTest[i], sentence, alignments)