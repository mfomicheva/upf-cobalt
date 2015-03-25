from wordSim import *
from ConfigParser import ConfigParser
from coreNlpUtil import *
import wordSim


class Scorer(object):

    alpha = 1
    delta = 1

    exact = 1
    stem = 1
    synonym = 1
    paraphrase = 1
    related = 1
    related_threshold = 1
    context_importance = 1

    def __init__(self):
        config = ConfigParser()
        config.readfp(open('Config/scorer.cfg'))

        self.alpha = config.getfloat('Scorer', 'alpha')
        self.delta = config.getfloat('Scorer', 'delta')

        self.exact = config.getfloat('Scorer', 'exact')
        self.stem = config.getfloat('Scorer', 'stem')
        self.synonym = config.getfloat('Scorer', 'synonym')
        self.paraphrase = config.getfloat('Scorer', 'paraphrase')
        self.related = config.getfloat('Scorer', 'related')
        self.related_threshold = config.getfloat('Scorer', 'related_threshold')
        self.context_importance = config.getfloat('Scorer', 'context_importance')


    # receives alignments structure as an input - alignments[0] is the aligned pair indexes,
    # alignments[1] is the aligned pair words, alignments[2] is the aligned pair dependency similarity score
    def calculateScore(self, sentence1, sentence2, alignments):
        sentence1 = prepareSentence2(sentence1)
        sentence2 = prepareSentence2(sentence2)

        functionalWords1 = filter(lambda x: wordSim.functionWord(x), sentence1)
        functionalWords2 = filter(lambda x: wordSim.functionWord(x), sentence2)

        weightedLength1 = self.delta * (len(sentence1) - len(functionalWords1)) + ((1.0 - self.delta) * len(functionalWords1))
        weightedLength2 = self.delta * (len(sentence2) - len(functionalWords2)) + ((1.0 - self.delta) * len(functionalWords2))

        weightedMatches1 = 0
        weightedMatches2 = 0

        for i, a in enumerate(alignments[0]):
            if not wordSim.functionWord(sentence1[a[0] - 1]):
                weightedMatches1 += self.delta * wordSim.maxWeightedWordRelatedness(sentence1[a[0] - 1], sentence2[a[1] - 1], self, alignments[2][i])
            else:
                weightedMatches1 += (1 - self.delta) * wordSim.maxWeightedWordRelatedness(sentence1[a[0] - 1], sentence2[a[1] - 1], self, alignments[2][i])

            if not wordSim.functionWord(sentence2[a[1] - 1]):
                weightedMatches2 += self.delta * wordSim.maxWeightedWordRelatedness(sentence1[a[0] - 1], sentence2[a[1] - 1], self, alignments[2][i])
            else:
                weightedMatches2 += (1 - self.delta) * wordSim.maxWeightedWordRelatedness(sentence1[a[0] - 1], sentence2[a[1] - 1], self, alignments[2][i])

        precision = weightedMatches1 / weightedLength1
        recall = weightedMatches2 / weightedLength2

        if precision == 0 or recall == 0:
            fMean = 0
        else:
            fMean = 1.0 / (((1.0 - self.alpha) / precision) + (self.alpha / recall))

        score = fMean

        return score