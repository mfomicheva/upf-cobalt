from aligner import *
from util import *
from scorer import *
import codecs
import re

# dir2processRef = '/Users/MarinaFomicheva/Dropbox/workspace/dataSets/wmt14-metrics-task/baselines/data/parsed/references'
# dir2processTest = '/Users/MarinaFomicheva/Dropbox/workspace/dataSets/wmt14-metrics-task/baselines/data/parsed/system-outputs/newstest2014/de-en'
# outputDir = '/Users/MarinaFomicheva/Dropbox/workspace/dataSets/wmt14-metrics-task/submissions/MWA/de-en'
# referenceFiles = readFileNames(open('Data/filesListReferences.txt'))
# testFiles = readFileNames(open('Data/filesListTest.txt'))
#
#
# for r in referenceFiles:
#
#     # if 'nc' in r:
#     #     dataSet = 'nc-test'
#     #     outputFileNameRef = 'news_'
#     # else:
#     #     dataSet = 'test'
#     #     outputFileNameRef = 'europarl_'
#
#     sentencesRef = readSentences(codecs.open(dir2processRef+'/'+r, encoding = 'UTF-8'))
#     dataset = 'newstest2014'
#     langPair = 'de-en'
#     metric = 'MWA'
#
#     outputFileScoring = open(outputDir + '/' + 'mwa.' + langPair + '.' + 'seg.score', 'w')
#
#     for t in testFiles:
#         # if (dataSet == 'nc-test' and 'nc' not in t) or (dataSet == 'test' and 'nc' in t):
#         #     continue
#         # outputFileNameTest=t
#         # outputFileScoring = open(outputDir + '/' + outputFileNameRef + outputFileNameTest +'.scoring.out', 'w')
#         # outputFileAlign = open(outputDir + '/' + outputFileNameRef + outputFileNameTest +'.align.out', 'w')
#         system=t
#         sentencesTest = readSentences(codecs.open(dir2processTest + '/' + dataset + '.' + t + '.' + langPair + '.out', encoding = 'UTF-8'))
#         aligner = Aligner('english')
#         scorer = Scorer()
#         outputFileAlign = open(outputDir + '/' + dataset + '.' + system + '.' + langPair + '.align.out', 'w')
#         for i, sentence in enumerate(sentencesRef):
#             phrase = i + 1
#             alignments = aligner.align(sentencesTest[i], sentence)
#             score = scorer.calculateScore(sentencesTest[i], sentence, alignments)
#
#             outputFileScoring.write(str(metric) + '\t' + str(langPair) + '\t' + str(dataset) + '\t' + str(system) + '\t' + str(phrase) + '\t' + str(score) + '\n')
#
#
#             for index in xrange(len(alignments[0])):
#                 outputFileAlign.write(str(alignments[0][index]) + " : " + str(alignments[1][index]) + " : " + str(alignments[2][index])+'\n')
#
#         outputFileAlign.close()
#     outputFileScoring.close()

sentencesRef = readSentences(codecs.open('Data/input-en-1.txt', encoding = 'UTF-8'))
sentencesTest = readSentences(codecs.open('Data/input-en-2.txt', encoding = 'UTF-8'))


scorer = Scorer()
aligner = Aligner('english',scorer)

for i, sentence in enumerate(sentencesRef):
    alignments = aligner.align(sentencesTest[i], sentence)

    ## print alignment and context information

    for index in xrange(len(alignments[0])):
          print str(alignments[0][index]) + " : " + str(alignments[1][index]) + " : " + str(alignments[2][index])

    print scorer.calculateScore(sentencesTest[i], sentence, alignments)