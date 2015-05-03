from aligner import *
from util import *
from scorer import *
import codecs
import getopt
import sys
from os import listdir
from os.path import isfile, join
from os.path import expanduser


home = expanduser("~")
referenceDir = home + '/Dropbox/workspace/dataSets/wmt14-metrics-task/baselines/data/parsed/references'
testDir = home + '/Dropbox/workspace/dataSets/wmt14-metrics-task/baselines/data/parsed/system-outputs'
outputDir = home + '/Dropbox/workspace/dataSets/wmt14-metrics-task/submissions/MWA/MWA-dep'
dataset = 'newstest2014'
metric = 'MWA-dep'


def main(args):

    opts, args = getopt.getopt(args, 'hl:m:a:', ['language=', 'maxsegments=', 'writealignments='])

    languagePair = ""
    maxSegments = 0
    writeAlignments = False

    for opt, arg in opts:
        if opt == '-h':
            print 'wmt2014 -l <language_pair>'
            sys.exit()
        elif opt in ('-l', '--language'):
            languagePair = arg
        elif opt in ('-m', '--maxsegments'):
            maxSegments = int(arg)
        elif opt in ('-a', '--writealignments'):
            writeAlignments = bool(arg)

    sentencesRef = readSentences(codecs.open(referenceDir + '/' + dataset + '-ref.' + languagePair + '.out', encoding='UTF-8'))

    outputFileScoring = open(outputDir + '/' + metric + '.' + languagePair + '.' + 'seg.score', 'w')

    testFiles = [f for f in listdir(testDir + '/' + dataset + '/' + languagePair) if isfile(join(testDir + '/' + dataset + '/' + languagePair, f))]

    scorer = Scorer()
    aligner = Aligner('english')

    for t in testFiles:
        print t
        system = t.split('.')[1] + '.' + t.split('.')[2]
        sentencesTest = readSentences(codecs.open(testDir + '/' + dataset + '/' + languagePair + '/' + t, encoding='UTF-8'))

        if (writeAlignments):
            outputFileAlign = open(outputDir + '/' + dataset + '.' + system + '.' + languagePair + '.align.out', 'w')

        for i, sentence in enumerate(sentencesRef):
            phrase = i + 1
            if maxSegments != 0 and phrase > maxSegments:
                continue

            # calculating alignment and score test to reference
            alignments1 = aligner.align(sentencesTest[i], sentence)
            score1 = scorer.calculateScore(sentencesTest[i], sentence, alignments1)

            if (writeAlignments):
                outputFileAlign.write('Sentence #' + str(phrase) + '\n')
                for index in xrange(len(alignments1[0])):
                    outputFileAlign.write(str(alignments1[0][index]) + " : " + str(alignments1[1][index]) + " : " + str(alignments1[2][index])+'\n')

            outputFileScoring.write(str(metric) + '\t' + str(languagePair) + '\t' + str(dataset) + '\t' + str(system) + '\t' + str(phrase) + '\t' + str(score1) + '\n')


        outputFileAlign.close()
    outputFileScoring.close()

if __name__ == "__main__":
    main(sys.argv[1:])