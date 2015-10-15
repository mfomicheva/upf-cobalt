from __future__ import division
from __future__ import print_function

from aligner import *
from util import *
from scorer import *
import codecs
from os import listdir
from os.path import isfile, join
import argparse
import numpy
from collections import OrderedDict
from coreNlpUtil import *
import testFeatures


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

    parser.add_argument("--metric",
            help="metric name",
            default="cobalt-testing",
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

class Features(object):

    def __init__(self, metric, dataset, langPair):
        self.data = OrderedDict()
        self.data['metric'] = metric
        self.data['dataset'] = dataset
        self.data['langPair'] = langPair
        self.data['system'] = ''
        self.data['phrase'] = 0
        self.data['bad_prop'] = 0.0
        self.data['good_prop'] = 0.0
        self.data['pen_count'] = 0.0
        self.data['pen_mean'] = 0.0
        self.data['pen_max'] = 0.0
        self.data['sim_mean'] = 0.0
        self.data['seg_len'] = 0.0
        self.data['score'] = 0.0

    def get_feats(self, system, phrase, length, alignments, word_level_scores, score, side):

        if side == 'test':
            len_aligned = len(set([x[0] for x in alignments[0]]))
        else:
            len_aligned = len(set([x[1] for x in alignments[0]]))

        self.data['system'] = system
        self.data['phrase'] = phrase
        self.data['bad_prop'] = (length - len_aligned) / length
        self.data['good_prop'] = len_aligned / length

        self.data['pen_count'] = len([getattr(item, 'penalty_' + side) for item in word_level_scores if getattr(item, 'penalty_' + side) > 0])
        if self.data['pen_count'] > 0:
            self.data['pen_mean'] = numpy.mean([getattr(item, 'penalty_' + side) for item in word_level_scores if getattr(item, 'penalty_' + side) > 0])
            self.data['pen_max'] = numpy.max([getattr(item, 'penalty_' + side) for item in word_level_scores if getattr(item, 'penalty_' + side) > 0])
        else:
            self.data['pen_mean'] = 0.0
            self.data['pen_max'] = 0.0

        if self.data['good_prop'] > 0:
            self.data['sim_mean'] = numpy.mean([getattr(item, 'similarity') for item in word_level_scores if getattr(item, 'similarity') > 0])
        else:
            self.data['sim_mean'] = 0.0


        self.data['seg_len'] = length
        self.data['score'] = score


def output(metric, output_dir, output_type, results):
    file = open(output_dir + '/' + metric + output_type, 'w')
    for line in results:
        file.write(line + '\n')

def normRefFile(ref_dir, dataset, langPair):

    if dataset == 'newstest2013':
        fileName = ref_dir + '/' + dataset + '/' + dataset + '-ref.' + langPair.split('-')[1] + '.out'
    elif dataset == 'newstest2015' or dataset == 'newsdiscusstest2015':
        fileName = ref_dir + '/' + dataset + '/' + dataset + '-' + langPair.split('-')[0] + langPair.split('-')[1] + '-ref.' + langPair.split('-')[1] + '.out'
    elif '2007' in dataset:
        fileName = ref_dir + '/' + dataset + '/' + dataset + '.' + langPair.split('-')[1] + '.out'
    elif 'ce_eamt' in dataset:
        fileName = ref_dir + '/' + dataset + '/' + langPair + '/target_postedited.out'
    else:
        fileName = ref_dir + '/' + dataset + '-ref.' + langPair + '.out'

    return fileName

def getSysName(testFileName, dataset, langPair):

    if dataset == 'newstest2013':
        sysName = re.sub('^%s\.%s\.(?P<name>.+)\.%s$' % (dataset, langPair, 'out'), '\g<name>', testFileName)
    elif '2007' in dataset:
        sysName = testFileName.split('.')[0]
    elif 'eamt' in dataset:
        sysName = 'smt'
    else:
        sysName = testFileName.split('.')[1] + '.' + testFileName.split('.')[2]

    return sysName

def makeHeaderScores():

    scores = ['metric', 'languagePair', 'dataset', 'system', 'phrase', 'score']
    return '\t'.join(str(x) for x in scores)

def main():

    metric = parameters.metric

    config = ConfigParser()
    config.readfp(open(parameters.config))

    reference_dir = config.get('Paths', 'reference_dir')
    test_dir = config.get('Paths', 'test_dir')
    output_dir = config.get('Paths', 'output_dir')
    ppdbFileName = config.get('Paths', 'ppdbFileName')
    vectorsFileName = config.get('Paths', 'vectorsFileName')

    loadPPDB(ppdbFileName)
    loadWordVectors(vectorsFileName)
    scorer = Scorer()
    aligner = Aligner('english')

    for dataset in parameters.datasets:
        for languagePair in parameters.directions:

            scores_file = open(output_dir + '/' + metric + '.' + languagePair + '.' + 'seg.score', 'w')
            feats_file_ref = open(output_dir + '/' + metric + '.' + languagePair + '.' + 'seg.feats.ref', 'w')
            feats_file_test = open(output_dir + '/' + metric + '.' + languagePair + '.' + 'seg.feats.test', 'w')

            makeHeaderScores()

            if (parameters.statistics):

                ref_feats = Features(metric, dataset, languagePair)
                test_feats = Features(metric, dataset, languagePair)

                print('\t'.join(str(x) for x in ref_feats.data.keys()), file = feats_file_ref)
                print('\t'.join(str(x) for x in ref_feats.data.keys()), file = feats_file_test)

            refFileName = normRefFile(reference_dir, dataset, languagePair)
            ref_data = readSentences(codecs.open(refFileName, encoding='UTF-8'))

            testFiles = [f for f in listdir(test_dir + '/' + dataset + '/' + languagePair) if isfile(join(test_dir + '/' + dataset + '/' + languagePair, f))]

            for t in testFiles:

                if t[0] == '.':
                    continue
                print(t)

                system = getSysName(t, dataset, languagePair)

                if (parameters.system_name) and not system == parameters.system_name:
                    continue

                test_data = readSentences(codecs.open(test_dir + '/' + dataset + '/' + languagePair + '/' + t, encoding='UTF-8'))

                if (parameters.alignments):
                    align_file = open(output_dir + '/' + dataset + '.' + system + '.' + languagePair + '.align.out', 'w')

                for i, phrase_ref in enumerate(ref_data):

                    num_phrase = i + 1
                    if parameters.max_segments != 0 and num_phrase > parameters.max_segments:
                        continue
                    if parameters.phrase_number != 0 and num_phrase != parameters.phrase_number:
                        continue

                    alignments = aligner.align(test_data[i], phrase_ref)

                    sentence1 = prepareSentence2(test_data[i])
                    sentence2 = prepareSentence2(phrase_ref)

                    word_level_scores = scorer.word_scores(sentence1, sentence2, alignments)
                    sentence_level_score = scorer.sentence_score_cobalt(sentence1, sentence2, alignments, word_level_scores)

                    if (parameters.alignments) or (parameters.contextInfo):
                        print('Sentence #' + str(num_phrase), file = align_file)

                        for index in xrange(len(alignments[0])):

                            if (parameters.contextInfo):
                                print(str(alignments[0][index]) + " : " + str(alignments[1][index]) + " : " + str(alignments[2][index]), file = align_file)
                            else:
                                print(str(alignments[0][index]) + " : " + str(alignments[1][index]) + " : " + str(word_level_scores[index].similarity) + " : " + str(word_level_scores[index].penalty_mean), file = align_file)

                    if (parameters.statistics):

                        testFeatures.computeFeatures(test_data[i], phrase_ref, sentence1, sentence2, alignments)

                        ref_feats.get_feats(system, num_phrase, scorer.sentence_length(phrase_ref), alignments, word_level_scores, sentence_level_score, 'ref')
                        test_feats.get_feats(system, num_phrase, scorer.sentence_length(test_data[i]), alignments, word_level_scores, sentence_level_score, 'test')

                        print('\t'.join(format_item(x[1]) for x in ref_feats.data.items()), file = feats_file_ref)
                        print('\t'.join(format_item(x[1]) for x in test_feats.data.items()), file = feats_file_test)

                    print(str(metric) + '\t' + str(languagePair) + '\t' + str(dataset) + '\t' + str(system) + '\t' + str(num_phrase) + '\t' + str(sentence_level_score), file = scores_file)

                if (parameters.alignments):
                    align_file.close()

            scores_file.close()
            feats_file_ref.close()
            feats_file_test.close()

def format_item(item):
    if isinstance(item, float):
        return "{0:.2f}".format(item)
    else:
        return str(item)

if __name__ == "__main__":
    main()
