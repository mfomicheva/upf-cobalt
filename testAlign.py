from aligner import *
from util import *
from scorer import *
import codecs
import re

sentencesRef = readSentences(codecs.open('Data/input-en-1.txt', encoding = 'UTF-8'))
sentencesTest = readSentences(codecs.open('Data/input-en-2.txt', encoding = 'UTF-8'))

aligner = Aligner('english')
scorer = Scorer()

for i, sentence in enumerate(sentencesRef):
    alignments = aligner.align(sentencesTest[i], sentence)

    ## print alignment and context information

    for index in xrange(len(alignments[0])):
          print str(alignments[0][index]) + "\t" + str(alignments[1][index]) + "\t" + str(alignments[2][index])

    print scorer.calculateScore(sentencesTest[i], sentence, alignments)