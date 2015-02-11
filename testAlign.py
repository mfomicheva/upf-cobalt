from aligner import *
from util import *
from scorer import *

sentences = readSentences(open('Data/input-en-1.txt'))
sentences2 = readSentences(open('Data/input-en-2.txt'))

aligner = Aligner('english')
scorer = Scorer()

for i, sentence in enumerate(sentences):
    alignments = aligner.align(sentence, sentences2[i])
    print alignments[0]
    print alignments[1]
    print alignments[2]

    print scorer.calculateScore(sentence, sentences2[i], alignments[0])