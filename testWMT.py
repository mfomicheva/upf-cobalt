from aligner import *
from util import *
from scorer import *
import codecs
import getopt
import sys
from os import listdir
from os.path import isfile, join
from os.path import expanduser
import argparse

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


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
            description="WMT evaluation"
            )

    parser.add_argument("--config",
            help="file with paths",
            required=True,
            metavar="FILE",
            type=str
            )

    parser.add_argument("--directions",
            help="translation directions",
            metavar="DIRECTION",
            default=["es-en"],
            nargs='*'
            )

    parser.add_argument("--datasets",
            help="datasets",
            metavar="DATASETS",
            nargs='*'
            )

    parser.add_argument("--phrase_number",
            help="Phrase to process",
            default=0,
            type=int,
            )

    parser.add_argument("--max_segments",
            help="maximum number of phrases",
            default=0,
            type=int,
            )

    parser.add_argument("--system_name",
            help="MT system",
            type=str,
            )

    parser.add_argument("--alignments",
            help="""for each aligned word pair, writes the indices of the words,
            word forms, lexical similarity and context penalty""",
            action = 'store_true',
            default=False,
            )

    parser.add_argument("--contextInfo",
            help="""for each aligned word pair, writes the indices of the words,
                 word forms and dependendency functions of the words constituting contextual difference""",
            action = 'store_true',
            default=False,
            )

    parser.add_argument("--statistics",
            help="""for each test case, writes the score,
                 average lexical similarity, average context penalty""",
            action = 'store_true',
            default=False,
            )

    return parser.parse_args()

parameters = parse_args()

def main():

    config = ConfigParser()
    config.readfp(open(parameters.config))

    reference_dir = config.get('Paths', 'reference_dir')
    test_dir = config.get('Paths', 'test_dir')
    output_dir = config.get('Paths', 'output_dir')
    metric = config.get('Paths', 'metric')
    ppdbFileName = config.get('Paths', 'ppdbFileName')
    vectorsFileName = config.get('Paths', 'vectorsFileName')


    loadPPDB(ppdbFileName)
    loadWordVectors(vectorsFileName)
    scorer = Scorer()
    aligner = Aligner('english')



    for dataset in parameters.datasets:
        for languagePair in parameters.directions:

            output_scoring = open(output_dir + '/' + metric + '.' + dataset + '.' + languagePair + '.' + 'seg.score', 'w')

            if (parameters.statistics):
                output_stats = open(output_dir + '/' + metric + '.' + dataset + '.' + languagePair + '.stats.out', 'w')

            sourceLanguage = languagePair.split('-')[0]
            targetLanguage = languagePair.split('-')[1]

            if dataset == 'newstest2013':
                sentencesRef = readSentences(codecs.open(reference_dir + '/' + dataset + '/' + dataset + '-ref.' + targetLanguage + '.out', encoding='UTF-8'))

            elif dataset == 'newstest2015' or dataset == 'newsdiscusstest2015':
                sentencesRef = readSentences(codecs.open(reference_dir + '/' + dataset + '/' + dataset + '-' + sourceLanguage + targetLanguage + '-ref.' + targetLanguage + '.out', encoding='UTF-8'))

            elif '2007' in dataset:
                sentencesRef = readSentences(codecs.open(reference_dir + '/' + dataset + '/' + dataset + '.' + targetLanguage + '.out', encoding='UTF-8'))

            else:
                sentencesRef = readSentences(codecs.open(reference_dir + '/' + dataset + '-ref.' + languagePair + '.out', encoding='UTF-8'))

            testFiles = [f for f in listdir(test_dir + '/' + dataset + '/' + languagePair) if isfile(join(test_dir + '/' + dataset + '/' + languagePair, f))]

            for t in testFiles:
                if t[0] == '.':
                    continue
                print t
                #check system names in the dataset!
                if dataset == 'newstest2013':
                    system = t.split('.')[2] + '.' + t.split('.')[3]
                elif '2007' in dataset:
                    system = t.split('.')[0]
                else:
                    system = t.split('.')[1] + '.' + t.split('.')[2]

                if (parameters.system_name) and not system == parameters.system_name:
                    continue

                sentencesTest = readSentences(codecs.open(test_dir + '/' + dataset + '/' + languagePair + '/' + t, encoding='UTF-8'))

                if (parameters.alignments):
                    output_alignment = open(output_dir + '/' + dataset + '.' + system + '.' + languagePair + '.align.out', 'w')

                for i, sentence in enumerate(sentencesRef):

                    lexSim_sum = 0
                    contextPen_sum = 0

                    phrase = i + 1
                    if parameters.max_segments != 0 and phrase > parameters.max_segments:
                        continue
                    if parameters.phrase_number != 0 and phrase != parameters.phrase_number:
                        continue

                    # calculating alignment and score test to reference
                    alignments1 = aligner.align(sentencesTest[i], sentence)
                    word_level_scores = scorer.word_level_scores(sentencesTest[i], sentence, alignments1)
                    sentence_level_score = scorer.sentence_level_score(sentencesTest[i], sentence, alignments1, word_level_scores)

                    if (parameters.alignments) or (parameters.contextInfo):
                        output_alignment.write('Sentence #' + str(phrase) + '\n')

                        for index in xrange(len(alignments1[0])):

                            if (parameters.statistics):
                                lexSim_sum += word_level_scores[0][index]
                                contextPen_sum += word_level_scores[1][index]

                            if (parameters.contextInfo):
                                output_alignment.write(str(alignments1[0][index]) + " : " + str(alignments1[1][index]) + " : " + str(alignments1[2][index]) + '\n')
                            else:
                                output_alignment.write(str(alignments1[0][index]) + " : " + str(alignments1[1][index]) + " : " + str(word_level_scores[0][index]) + " : " + str(word_level_scores[1][index]) + '\n')

                    if (parameters.statistics):

                        sentence_length_ref = scorer.sentence_length(sentence)
                        sentence_length_sys = scorer.sentence_length(sentencesTest[i])


                        if len(alignments1[0]) > 0:
                            lexSim_mean = lexSim_sum/len(alignments1[0])
                            contextPen_mean = contextPen_sum/len(alignments1[0])
                            non_aligned_ref = (sentence_length_ref - len(alignments1[0]))/len(alignments1[0])
                            non_aligned_sys = (sentence_length_sys - len(alignments1[0]))/len(alignments1[0])
                        else:

                            lexSim_mean = 0
                            contextPen_mean = 0
                            non_aligned_ref = 0
                            non_aligned_sys = 0

                        output_stats.write(str(metric) + '\t' + str(languagePair) + '\t' + str(dataset) + '\t' + str(system) + '\t' + str(phrase) + '\t' + str(sentence_level_score) \
                                       + '\t' + str(lexSim_mean) + '\t' + str(contextPen_mean) \
                                       + '\t' + str(non_aligned_ref) \
                                       + '\t' + str(non_aligned_sys) + '\n')
                    else:
                        output_scoring.write(str(metric) + '\t' + str(languagePair) + '\t' + str(dataset) + '\t' + str(system) + '\t' + str(phrase) + '\t' + str(sentence_level_score) + '\n')

                if (parameters.alignments):
                    output_alignment.close()

            output_scoring.close()



if __name__ == "__main__":
    main()
