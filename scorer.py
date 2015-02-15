from wordSim import *
from ConfigParser import ConfigParser
from coreNlpUtil import *


class Scorer(object):

    alpha = 1

    beta = 1

    gamma = 1

    delta = 1
    
    exact = 1

    stem = 1

    synonym = 1

    paraphrase = 1

    def __init__(self):
        config = ConfigParser()
        config.readfp(open('Config/scorer.cfg'))

        self.alpha = config.getfloat('Scorer', 'alpha')
        self.beta = config.getfloat('Scorer', 'beta')
        self.gamma = config.getfloat('Scorer', 'gamma')
        self.delta = config.getfloat('Scorer', 'delta')
        self.exact = config.getfloat('Scorer', 'exact')
        self.stem = config.getfloat('Scorer', 'stem')
        self.synonym = config.getfloat('Scorer', 'synonym')
        self.paraphrase = config.getfloat('Scorer', 'paraphrase')

    def __calculateChuncks(self, sentence1, sentence2, alignments):
        sortedAlignments = sorted(alignments, key=lambda alignment: alignment[0])

        chunks = 0

        previousPair = None

        for pair in sortedAlignments:
            if previousPair == None or previousPair[0] != pair[0] - 1 or previousPair[1] != pair[1] - 1:
                chunks += 1

            previousPair = pair

        return chunks

    # receives alignments structure as an input - alignments[0] is the aligned pair indexes,
    # alignments[1] is the aligned pair words, alignments[3] is the aligned pair dependency similarity score
    def calculateScore(self, sentence1, sentence2, alignments):
        sentence1 = prepareSentence(sentence1)
        sentence2 = prepareSentence(sentence2)

        functionalWords1 = filter(lambda x: functionWord(x), sentence1)
        functionalWords2 = filter(lambda x: functionWord(x), sentence2)

        weightedLength1 = self.delta * (len(sentence1) - len(functionalWords1)) + ((1.0 - self.delta) * len(functionalWords1))
        weightedLength2 = self.delta * (len(sentence2) - len(functionalWords2)) + ((1.0 - self.delta) * len(functionalWords2))

        weightedMatches1 = 0
        weightedMatches2 = 0

        for i, a in enumerate(alignments[0]):
            if not functionWord(sentence1[a[0] - 1]):
                weightedMatches1 += self.delta * weightedWordRelatedness(sentence1[a[0] - 1], sentence2[a[1] - 1], self.exact, self.stem, self.synonym, alignments[2][i])
            else:
                weightedMatches1 += (1 - self.delta) * weightedWordRelatedness(sentence1[a[0] - 1], sentence2[a[1] - 1], self.exact, self.stem, self.synonym, alignments[2][i])

            if not functionWord(sentence2[a[1] - 1]):
                weightedMatches2 += self.delta * weightedWordRelatedness(sentence1[a[0] - 1], sentence2[a[1] - 1], self.exact, self.stem, self.synonym, alignments[2][i])
            else:
                weightedMatches2 += (1 - self.delta) * weightedWordRelatedness(sentence1[a[0] - 1], sentence2[a[1] - 1], self.exact, self.stem, self.synonym, alignments[2][i])

        precision = weightedMatches1 / weightedLength1
        recall = weightedMatches2 / weightedLength2

        f1 = (2 * precision * recall) / (precision + recall)

        fMean = 1.0 / (((1.0 - self.alpha) / precision) + (self.alpha / recall))

        fragPenalty = 0

        chunckNumber = self.__calculateChuncks(sentence1, sentence2, alignments[0])

        if chunckNumber > 1:
            fragPenalty = self.gamma * pow(float(chunckNumber) / len(alignments[0]), self.beta)

        score = fMean * (1.0 - fragPenalty)

        return score