from aligner import *
from util import *

sentences = readSentences(open('Data/input-en-1.txt'))
sentences2 = readSentences(open('Data/input-en-2.txt'))

for i, sentence in enumerate(sentences):
    aligner = Aligner('english')
    alignments = aligner.align(sentence, sentences2[i])
    print alignments[0]
    print alignments[1]