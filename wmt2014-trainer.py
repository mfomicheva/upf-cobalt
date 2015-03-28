from aligner import *
from util import *
from scorer import *
from reader import *
import codecs
import getopt
import sys
from os import listdir
from os.path import isfile, join
from os.path import expanduser


home = expanduser("~")
referenceDir = home + '/Dropbox/dataSets/wmt14-metrics-task/baselines/data/parsed/references'
testDir = home + '/Dropbox/dataSets/wmt14-metrics-task/baselines/data/parsed/system-outputs'
outputDir = home + '/Dropbox/dataSets/wmt14-metrics-task/submissions/MWA/MWA-WORDNET-MIN'
dataset = 'newstest2014'
metric = 'MWA'

def main(args):

    opts, args = getopt.getopt(args, 'hl:m:a:', ['language=', 'maxsegments=', 'writealignments='])

    languagePair = ""

    for opt, arg in opts:
        if opt == '-h':
            print 'reader.py -l <language_pair>'
            sys.exit()
        elif opt in ('-l', '--language'):
            languagePair = arg

    sentencesRef = readSentences(codecs.open(referenceDir + '/' + dataset + '-ref.' + languagePair + '.out', encoding='UTF-8'))

    outputFileScoring = open(outputDir + '/' + 'mwa-trained-wordnet-min.' + languagePair + '.' + 'seg.score', 'w')

    testFiles = [f for f in listdir(testDir + '/' + dataset + '/' + languagePair) if isfile(join(testDir + '/' + dataset + '/' + languagePair, f))]

    scorer = Scorer()
    aligner = Aligner('english')
    reader = Reader()

    for t in testFiles:
        system = t.split('.')[1] + '.' + t.split('.')[2]
        sentencesTest = readSentences(codecs.open(testDir + '/' + dataset + '/' + languagePair + '/' + t, encoding='UTF-8'))
        alignment_file = outputDir + '/' + dataset + '.' + system + '.' + languagePair + '.align.out'
        alignments = reader.read(alignment_file)

        for i, sentence in enumerate(sentencesRef):
            phrase = i + 1
            score = scorer.calculateScore(sentencesTest[i], sentence, alignments[phrase])
            outputFileScoring.write(str(metric) + '\t' + str(languagePair) + '\t' + str(dataset) + '\t' + str(system) + '\t' + str(phrase) + '\t' + str(score) + '\n')

    outputFileScoring.close()

if __name__ == "__main__":
    main(sys.argv[1:])