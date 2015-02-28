from aligner import *
from util import *
from scorer import *
import re

#sentences = readSentences(open('Data/systran.es-en.test.primary.txt.out'))
#sentences = readSentences(open('/Users/MarinaFomicheva/Dropbox/workspace/dataSets/wmt2007-data/es-en_judged/parsed/systran.es-en.test.primary.txt.out'))
#sentences2 = readSentences(open('/Users/MarinaFomicheva/Dropbox/workspace/dataSets/wmt2007-data/es-en_judged/parsed/test2007.en.out'))

# dir2process = '/Users/MarinaFomicheva/Dropbox/workspace/dataSets/wmt2007-data/es-en_judged/parsed'
# outputDir = '/Users/MarinaFomicheva/Dropbox/workspace/dataSets/wmt2007-data/tmp'
# referenceFiles = readFileNames(open('Data/filesListReferences.txt'))
# testFiles = readFileNames(open('Data/filesListTest.txt'))
#
#
# for r in referenceFiles:
#
#     if 'nc' in r:
#         dataSet = 'nc-test'
#         outputFileNameRef = 'news_'
#     else:
#         dataSet = 'test'
#         outputFileNameRef = 'europarl_'
#
#     sentences = readSentences(open(dir2process+'/'+r))
#     for t in testFiles:
#         if (dataSet == 'nc-test' and 'nc' not in t) or (dataSet == 'test' and 'nc' in t):
#             continue
#         outputFileNameTest=t
#         outputFileScoring = open(outputDir + '/' + outputFileNameRef + outputFileNameTest +'.scoring.out', 'w')
#         outputFileAlign = open(outputDir + '/' + outputFileNameRef + outputFileNameTest +'.align.out', 'w')
#         sentences2 = readSentences(open(dir2process+'/'+t))
#         aligner = Aligner('english')
#         scorer = Scorer()
#         for i, sentence in enumerate(sentences):
#             alignments = aligner.align(sentence.decode('UTF-8'), sentences2[i].decode('UTF-8'))
#             score = scorer.calculateScore(sentence, sentences2[i], alignments)
#             outputFileScoring.write(str(score) + '\n')
#             for index in xrange(len(alignments[0])):
#                 outputFileAlign.write(str(alignments[0][index]) + " : " + str(alignments[1][index]) + " : " + str(alignments[2][index])+'\n')
#
#         outputFileScoring.close()
#         outputFileAlign.close()




sentences = readSentences(open('Data/input-en-1.txt'))
sentences2 = readSentences(open('Data/input-en-2.txt'))

aligner = Aligner('english')
scorer = Scorer()

for i, sentence in enumerate(sentences):
    alignments = aligner.align(sentence.decode('UTF-8'), sentences2[i].decode('UTF-8'))

    ## print alignment and context information
    for index in xrange(len(alignments[0])):
          print str(alignments[0][index]) + " : " + str(alignments[1][index]) + " : " + str(alignments[2][index])

    print scorer.calculateScore(sentence, sentences2[i], alignments)