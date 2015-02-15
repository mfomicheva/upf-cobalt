from aligner import *
from util import *
from scorer import *

sentences = readSentences(open('test.en-es.txt.out'))
sentences2 = readSentences(open('reference.en-es.txt.out'))

#sentences = readSentences(open('Data/input-en-1.txt'))
#sentences2 = readSentences(open('Data/input-en-2.txt'))

aligner = Aligner('english')
scorer = Scorer()

for i, sentence in enumerate(sentences):
    alignments = aligner.align(sentence.decode('UTF-8'), sentences2[i].decode('UTF-8'))

    #for index in xrange(len(alignments[0])):
    #    print str(alignments[0][index]) + " : " + str(alignments[1][index]) + " : " + str(alignments[2][index])

    print scorer.calculateScore(sentence, sentences2[i], alignments)