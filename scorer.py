from wordSim import *
from ConfigParser import ConfigParser
from coreNlpUtil import *
import wordSim
import math
from json import *


class Scorer(object):

    alpha = 1
    beta = 1
    delta = 1

    exact = 1
    stem = 1
    synonym = 1
    paraphrase = 1
    posExact = 1
    posGramCat = 1
    posNone = 1
    related = 1
    related_threshold = 1
    context_importance = 1
    minimal_aligned_relatedness = 1

    arguments = 1
    modifiers = 1
    function = 1

    argument_types = []
    modifier_types = []
    function_types = []

    def __init__(self):
        config = ConfigParser()
        config.readfp(open('Config/scorer.cfg'))

        self.alpha = config.getfloat('Scorer', 'alpha')
        self.beta = config.getfloat('Scorer', 'beta')
        self.delta = config.getfloat('Scorer', 'delta')

        self.exact = config.getfloat('Scorer', 'exact')
        self.stem = config.getfloat('Scorer', 'stem')
        self.synonym = config.getfloat('Scorer', 'synonym')
        self.paraphrase = config.getfloat('Scorer', 'paraphrase')

        self.related = config.getfloat('Scorer', 'related')
        self.related_threshold = config.getfloat('Scorer', 'related_threshold')
        self.context_importance = config.getfloat('Scorer', 'context_importance')
        self.minimal_aligned_relatedness = config.getfloat('Scorer', 'minimal_aligned_relatedness')

        self.arguments = config.getfloat('Dependency Weights', 'arguments')
        self.modifiers = config.getfloat('Dependency Weights', 'modifiers')
        self.function = config.getfloat('Dependency Weights', 'function')

        self.argument_types = loads(config.get('Dependency Types', 'arguments'))
        self.modifier_types = loads(config.get('Dependency Types', 'modifiers'))
        self.function_types = loads(config.get('Dependency Types', 'function'))


    def get_dependency_weight(self, dependency_label):

        if dependency_label.split('_')[0] in self.argument_types:
            return self.arguments

        elif dependency_label.split('_')[0] in self.modifier_types:
            return self.modifiers

        else:
            return self.function

    def sum_dependency_weights(self, dependencies):
        result = 0
        for d in dependencies:
            result += self.get_dependency_weight(d)

        return result

    def calculate_context_penalty(self, context_info):
        source_diff = self.sum_dependency_weights(context_info['srcDiff'])
        target_diff = self.sum_dependency_weights(context_info['tgtDiff'])
        source_length = self.sum_dependency_weights(context_info['srcCon'])
        target_length = self.sum_dependency_weights(context_info['tgtCon'])

        penalty = self.calculate_context_difference_mean(source_diff, target_diff, source_length, target_length) * math.log(target_length + 1.0)
        penalty = (1.0/(1.0 + math.exp(-penalty)))
        penalty = 2 * penalty - 1

        return penalty


    def calculate_context_difference_mean(self, source_diff, target_diff, source_length, target_length):

        precision = 0.0
        recall = 0.0
        fscore = 0.0

        if source_length > 0 and target_length > 0:

            precision += source_diff/source_length
            recall += target_diff/target_length

            if precision == 0 or recall == 0:
                return max(precision, recall)
            else:
                fscore += (1 + math.pow(self.beta, 2)) * \
                          (precision * recall/((precision * math.pow(self.beta, 2)) + recall))

        return fscore

    # receives alignments structure as an input - alignments[0] is the aligned pair indexes,
    # alignments[1] is the aligned pair words, alignments[2] is the aligned pair dependency difference structure
    def word_level_scores(self, sentence1, sentence2, alignments):
        lexsimilarities = []
        penalties = []

        sentence1 = prepareSentence2(sentence1)
        sentence2 = prepareSentence2(sentence2)

        for i, a in enumerate(alignments[0]):
            lexsimilarities.append(wordSim.wordRelatednessScoring(sentence1[a[0] - 1], sentence2[a[1] - 1], self))
            penalties.append(self.calculate_context_penalty(alignments[2][i]))

        return [lexsimilarities, penalties]

    def sentence_level_score(self, sentence1, sentence2, alignments, word_level_scores):

        sentence1 = prepareSentence2(sentence1)
        sentence2 = prepareSentence2(sentence2)

        functional_words1 = filter(lambda x: wordSim.functionWord(x.form), sentence1)
        functional_words2 = filter(lambda x: wordSim.functionWord(x.form), sentence2)

        weighted_length1 = self.delta * (len(sentence1) - len(functional_words1)) + ((1.0 - self.delta) * len(functional_words1))
        weighted_length2 = self.delta * (len(sentence2) - len(functional_words2)) + ((1.0 - self.delta) * len(functional_words2))

        weighted_matches1 = 0
        weighted_matches2 = 0

        for i, a in enumerate(alignments[0]):

            if not wordSim.functionWord(sentence1[a[0] - 1].form):
                weighted_matches1 += self.delta * (max(word_level_scores[0][i] - word_level_scores[1][i], self.minimal_aligned_relatedness))
            else:
                weighted_matches1 += (1 - self.delta) * (max(word_level_scores[0][i] - word_level_scores[1][i], self.minimal_aligned_relatedness))

            if not wordSim.functionWord(sentence2[a[1] - 1].form):
                weighted_matches2 += self.delta * (max(word_level_scores[0][i] - word_level_scores[1][i], self.minimal_aligned_relatedness))
            else:
                weighted_matches2 += (1 - self.delta) * (max(word_level_scores[0][i] - word_level_scores[1][i], self.minimal_aligned_relatedness))

        if weighted_length1 == 0:
            precision = weighted_matches1
        else:
            precision = weighted_matches1 / weighted_length1

        if weighted_length2 == 0:
            recall = weighted_matches2
        else:
            recall = weighted_matches2 / weighted_length2

        if precision == 0 or recall == 0 or (((1.0 - self.alpha) / precision) + (self.alpha / recall)) == 0:
            fmean = 0
        else:
            fmean = 1.0 / (((1.0 - self.alpha) / precision) + (self.alpha / recall))

        score = fmean

        return score