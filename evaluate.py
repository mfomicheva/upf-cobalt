__author__ = 'MarinaFomicheva'

from aligner import *
from util import *
from scorer import *
import codecs
import getopt
import sys
from os import listdir
from os.path import isfile, join
from os.path import expanduser

def loadPPDB(ppdbFileName):

    global ppdbDict

    count = 0

    ppdbFile = open(ppdbFileName, 'r')
    for line in ppdbFile:
        if line == '\n':
            continue
        tokens = line.split()
        tokens[1] = tokens[1].strip()
        ppdbDict[(tokens[0], tokens[1])] = 0.6
        count += 1

def loadWordVectors(vectorsFileName):

    global wordVector
    vectorFile = open (vectorsFileName, 'r')

    for line in vectorFile:
        if line == '\n':
            continue

        match = re.match(r'^([^ ]+) (.+)',line)
        if type(match) is NoneType:
            continue

        word = match.group(1)
        vector = match.group(2)

        wordVector[word] = vector

def main(args):

    reference_file = ''
    test_file = ''
    output_directory = ''
    writeAlignments = False
    vectorsFileName = ''

    opts, args = getopt.getopt(args, 'hr:t:v:a:o:', ['reference=', 'test=', 'vectors_file=', 'writealignments=', 'output_directory='])

    for opt, arg in opts:
        if opt == '-h':
            print '-r <reference_file>'
            print '-t <test_file>'
            sys.exit()
        elif opt in ('-r', '--reference'):
            reference_file = arg
        elif opt in ('-t', '--test'):
            test_file = arg
        elif opt in ('-v', '--vectors_file'):
            vectorsFileName = arg
        elif opt in ('-a', '--writealignments'):
            writeAlignments = bool(arg)
        elif opt in ('-o', '--output_directory'):
            output_directory = arg

    if len(opts) == 0:
        reference_file = './Data/reference'
        test_file = 'Data/test'
        writeAlignments = True
        output_directory = './Data'

    metric = 'upf-cobalt'

    ppdbFileName = './Resources/ppdb-1.0-xxxl-lexical.extended.synonyms.uniquepairs'
    loadPPDB(ppdbFileName)
    if (vectorsFileName): loadWordVectors(vectorsFileName)

    sentences_ref = readSentences(codecs.open(reference_file, encoding='UTF-8'))
    sentences_test = readSentences(codecs.open(test_file, encoding='UTF-8'))

    output_scoring = open(output_directory + '/' + metric + '.seg.score', 'w')
    if (writeAlignments): output_alignment = open(output_directory + '/' + metric + '.align.out', 'w')

    scorer = Scorer()
    aligner = Aligner('english')

    for i, sentence in enumerate(sentences_ref):
        phrase = i + 1

        sentence1 = prepareSentence2(sentences_test[i])
        sentence2 = prepareSentence2(sentence)

        alignments = aligner.align(sentences_test[i], sentence)
        word_level_scores = scorer.word_scores(sentence1, sentence2, alignments)
        score1 = scorer.sentence_score_cobalt(sentence1, sentence2, alignments, word_level_scores)

        if (writeAlignments):
            output_alignment.write('Sentence #' + str(phrase) + '\n')

            for index in xrange(len(alignments[0])):
                output_alignment.write("{} \t {} \t {:.2f} \n".format(alignments[0][index], alignments[1][index], word_level_scores[index].penalty_mean))

        output_scoring.write(str(phrase) + '\t' + str(score1) + '\n')

    if (writeAlignments):
        output_alignment.close()

    output_scoring.close()

if __name__ == "__main__":
    main(sys.argv[1:])
