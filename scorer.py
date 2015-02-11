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


    def calculateScore(self, sentence1, sentence2, alignments):
        sentence1 = prepareSentence(sentence1)
        sentence2 = prepareSentence(sentence2)

        contentWords1 = filter(lambda x: not functionWord(x), sentence1)
        contentWords2 = filter(lambda x: not functionWord(x), sentence2)
        functionalWords1 = filter(lambda x: functionWord(x), sentence1)
        functionalWords2 = filter(lambda x: functionWord(x), sentence2)

        weightedLength1 = self.delta * (len(sentence1) - len(functionalWords1)) + ((1.0 - self.delta) * len(functionalWords1))
        weightedLength2 = self.delta * (len(sentence2) - len(functionalWords2)) + ((1.0 - self.delta) * len(functionalWords2))

        weightedMatches1 = 0
        weightedMatches2 = 0

        for pair in alignments:
            if not functionWord(sentence1[pair[0] - 1]):
                weightedMatches1 += self.delta * weightedWordRelatedness(sentence1[pair[0] - 1], sentence2[pair[1] - 1], self.exact, self.stem, self.synonym)
            else:
                weightedMatches1 += (1 - self.delta) * weightedWordRelatedness(sentence1[pair[0] - 1], sentence2[pair[1] - 1], self.exact, self.stem, self.synonym)

            if not functionWord(sentence2[pair[1] - 1]):
                weightedMatches2 += self.delta * weightedWordRelatedness(sentence1[pair[0] - 1], sentence2[pair[1] - 1], self.exact, self.stem, self.synonym)
            else:
                weightedMatches2 += (1 - self.delta) * weightedWordRelatedness(sentence1[pair[0] - 1], sentence2[pair[1] - 1], self.exact, self.stem, self.synonym)

        precision = weightedMatches1 / weightedLength1
        recall = weightedMatches2 / weightedLength2
        f1 = (2 * precision * recall) / (precision + recall)

        fMean = 1.0 / (((1.0 - self.alpha) / precision) + (self.alpha /recall))

        fragPenalty = 0

		# // Fragmentation
		# double frag;
		# // Case if test = ref
		# if (stats.testTotalMatches == stats.testLength
		# 		&& stats.referenceTotalMatches == stats.referenceLength
		# 		&& stats.chunks == 1)
		# 	frag = 0;
		# else
		# 	frag = ((double) stats.chunks)
		# 			/ (((double) (stats.testWordMatches + stats.referenceWordMatches)) / 2);
		# // Fragmentation penalty
		# stats.fragPenalty = gamma * Math.pow(frag, beta);

        score = fMean * (1.0 - fragPenalty)

        return score