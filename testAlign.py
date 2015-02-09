from aligner import *
from util import *

sentences = readSentences(open('Data/input-es-1.txt'))
sentences2 = readSentences(open('Data/input-es-2.txt'))

for i, sentence in enumerate(sentences):
    aligner = Aligner('spanish')
    alignments = aligner.align(sentence, sentences2[i])
    print alignments[0]
    print alignments[1]
    print alignments[2]