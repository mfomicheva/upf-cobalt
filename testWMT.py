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

def main(args):

    config_file_name = ''
    languagePair = ''
    maxSegments = 0
    writeAlignments = False

    opts, args = getopt.getopt(args, 'h:cfg:l:m:a:', ['configurationfile=', 'language=', 'maxsegments=', 'writealignments='])

    for opt, arg in opts:
        if opt == '-h':
            print 'wmt2014 -l <language_pair>'
            sys.exit()
        elif opt in ('-cfg', '--configurationfile'):
            config_file_name = arg
        elif opt in ('-l', '--language'):
            languagePair = arg
        elif opt in ('-m', '--maxsegments'):
            maxSegments = int(arg)
        elif opt in ('-a', '--writealignments'):
            writeAlignments = bool(arg)

    config = ConfigParser()
    config_file = config.readfp(open(config_file_name))

    if config.dataset == 'newstest2013':
        targetLanguage = languagePair.split('-')[1]
        sentencesRef = readSentences(codecs.open(config.reference_dir + '/' + config.dataset + '-ref.' + targetLanguage + '.out', encoding='UTF-8'))
    else:
        sentencesRef = readSentences(codecs.open(config.reference_dir + '/' + config.dataset + '-ref.' + languagePair + '.out', encoding='UTF-8'))

    output_scoring = open(config.output_dir + '/' + config.metric + '.' + languagePair + '.' + 'seg.score', 'w')

    testFiles = [f for f in listdir(config.test_dir + '/' + config.dataset + '/' + languagePair) if isfile(join(config.test_dir + '/' + config.dataset + '/' + languagePair, f))]

    scorer = Scorer()
    aligner = Aligner('english')

    for t in testFiles:
        print t
        system = t.split('.')[1] + '.' + t.split('.')[2]
        sentencesTest = readSentences(codecs.open(config.test_dir + '/' + config.dataset + '/' + languagePair + '/' + t, encoding='UTF-8'))

        if (writeAlignments):
            output_alignment = open(config.output_dir + '/' + config.dataset + '.' + system + '.' + languagePair + '.align.out', 'w')

        for i, sentence in enumerate(sentencesRef):
            phrase = i + 1
            if maxSegments != 0 and phrase > maxSegments:
                continue

            # calculating alignment and score test to reference
            alignments1 = aligner.align(sentencesTest[i], sentence)
            score1 = scorer.calculateScore(sentencesTest[i], sentence, alignments1)

            if (writeAlignments):
                output_alignment.write('Sentence #' + str(phrase) + '\n')
                for index in xrange(len(alignments1[0])):
                    output_alignment.write(str(alignments1[0][index]) + " : " + str(alignments1[1][index]) + " : " + str(alignments1[2][index]) + '\n')
                    for labelList in alignments1[3][index].keys():
                        if len(alignments1[3][index][labelList]) > 0:
                            output_alignment.write(str(labelList) + ': ' + ', '.join(alignments1[3][index][labelList]).encode('utf-8') + '\n')
                        else:
                            output_alignment.write(str(labelList) + ': ' + 'None' + '\n')

            output_scoring.write(str(config.metric) + '\t' + str(languagePair) + '\t' + str(config.dataset) + '\t' + str(system) + '\t' + str(phrase) + '\t' + str(score1) + '\n')


        if (writeAlignments):
            output_alignment.close()
    output_scoring.close()

if __name__ == "__main__":
    main(sys.argv[1:])



