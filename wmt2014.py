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
referenceDir = home + '/Dropbox/dataSets/wmt14-metrics-task/baselines/data/parsed/references'
testDir = home + '/Dropbox/dataSets/wmt14-metrics-task/baselines/data/parsed/system-outputs'
outputDir = home + '/Dropbox/dataSets/wmt14-metrics-task/submissions/MWA/'
dataset = 'newstest2014'
metric = 'MWA'


def main(args):

    opts, args = getopt.getopt(args, "hl:", ["language="])

    languagePair = ""

    for opt, arg in opts:
        if opt == '-h':
            print 'wmt2014 -l <language_pair>'
            sys.exit()
        elif opt in ("-l", "--language"):
            languagePair = arg

    sentencesRef = readSentences(codecs.open(referenceDir + '/' + dataset + '-ref.' + languagePair + '.out', encoding='UTF-8'))

    outputFileScoring = open(outputDir + '/' + 'mwa-without-wordnet.' + languagePair + '.' + 'seg.score', 'w')

    testFiles = [f for f in listdir(testDir + '/' + dataset + '/' + languagePair) if isfile(join(testDir + '/' + dataset + '/' + languagePair, f))]

    for t in testFiles:
        system = t.split('.')[1] + t.split('.')[2]
        sentencesTest = readSentences(codecs.open(testDir + '/' + dataset + '/' + languagePair + '/' + t, encoding='UTF-8'))
        scorer = Scorer()
        aligner = Aligner('english', scorer)
        outputFileAlign = open(outputDir + '/' + dataset + '.' + system + '.' + languagePair + '.align.out', 'w')

        for i, sentence in enumerate(sentencesRef):
            phrase = i + 1
            alignments = aligner.align(sentencesTest[i], sentence)
            score = scorer.calculateScore(sentencesTest[i], sentence, alignments)

            outputFileScoring.write(str(metric) + '\t' + str(languagePair) + '\t' + str(dataset) + '\t' + str(system) + '\t' + str(phrase) + '\t' + str(score) + '\n')

            for index in xrange(len(alignments[0])):
                outputFileAlign.write(str(alignments[0][index]) + " : " + str(alignments[1][index]) + " : " + str(alignments[2][index])+'\n')

        outputFileAlign.close()
    outputFileScoring.close()

if __name__ == "__main__":
   main(sys.argv[1:])