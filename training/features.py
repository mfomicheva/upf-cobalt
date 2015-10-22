__author__ = 'u88591'

import wordSim
import config
import scorer
import math
import numpy
from abstract_feature import *

class CountWordsTest(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'count_words_test')
        AbstractFeature.set_description(self, "Number of words in the candidate")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):
         AbstractFeature.set_value(self, len(candidate_parsed))


class CountWordsRef(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'count_words_ref')
        AbstractFeature.set_description(self, "Number of words in the reference")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):
         AbstractFeature.set_value(self, len(reference_parsed))


class CountContentTest(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'count_content_test')
        AbstractFeature.set_description(self, "Number of content words in the candidate")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):
        count = 0

        for word in candidate_parsed:
            if not wordSim.functionWord(word.form):
                count += 1

        AbstractFeature.set_value(self, count)


class CountContentRef(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'count_content_ref')
        AbstractFeature.set_description(self, "Number of content words in the reference")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):
        count = 0

        for word in reference_parsed:
             if not wordSim.functionWord(word.form):
                 count += 1

        AbstractFeature.set_value(self, count)


class CountFunctionTest(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'count_function_test')
        AbstractFeature.set_description(self, "Number of function words in the candidate")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):
        count = 0

        for word in candidate_parsed:
            if wordSim.functionWord(word.form):
                count += 1

        AbstractFeature.set_value(self, count)


class CountFunctionRef(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'count_function_ref')
        AbstractFeature.set_description(self, "Number of function words in the reference")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):
        count = 0

        for word in reference_parsed:
            if wordSim.functionWord(word.form):
                count += 1

        AbstractFeature.set_value(self, count)


class CountAligned(AbstractFeature):

    def __init__(self):
       AbstractFeature.__init__(self)
       AbstractFeature.set_name(self, 'count_aligned')
       AbstractFeature.set_description(self, "Number of aligned words")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):
        AbstractFeature.set_value(self, len(alignments[0]))


class PropAlignedTest(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'prop_aligned_test')
        AbstractFeature.set_description(self, "Proportion of aligned words in the candidate")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        if len(candidate_parsed) > 0:
            AbstractFeature.set_value(self, len(alignments[0]) / float(len(candidate_parsed)))
        else:
            AbstractFeature.set_value(self, 0)


class PropAlignedRef(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'prop_aligned_ref')
        AbstractFeature.set_description(self, "Proportion of aligned words in the reference")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        if len(reference_parsed) > 0:
            AbstractFeature.set_value(self, len(alignments[0]) / float(len(reference_parsed)))
        else:
            AbstractFeature.set_value(self, 0)


class PropAlignedContent(AbstractFeature):

    ## Supposing content words can only be aligned to content words

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'prop_aligned_content')
        AbstractFeature.set_description(self, "Proportion of aligned content words")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        if len(alignments[0]) > 0:
            count = 0

            for word in alignments[1]:
                if word[0] not in config.stopwords and word[0] not in config.punctuations:
                    count += 1

            AbstractFeature.set_value(self, count / float(len(alignments[0])))
        else:
            AbstractFeature.set_value(self, 0)


class PropAlignedFunction(AbstractFeature):

    ## Supposing content words can only be aligned to content words

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'prop_aligned_function')
        AbstractFeature.set_description(self, "Proportion of aligned function words")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        if len(alignments[0]) > 0:
            count = 0
            for word in alignments[1]:
                if word[0] in config.stopwords or word[0] in config.punctuations:
                    count += 1

            AbstractFeature.set_value(self, count / float(len(alignments[0])))
        else:
            AbstractFeature.set_value(self, 0)


class PropAlignedExactExact(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'prop_aligned_exact_exact')
        AbstractFeature.set_description(self, "Proportion of aligned words with exact lexical match and exact POS match")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        if len(alignments[0]) > 0:
            count = 0

            for index in alignments[0]:
                word_candidate = candidate_parsed[index[0] - 1]
                word_reference = reference_parsed[index[1] - 1]

                if wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Exact':
                    count += 1

            AbstractFeature.set_value(self, count / float(len(alignments[0])))
        else:
            AbstractFeature.set_value(self, 0)


class PropAlignedSynExact(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'prop_aligned_syn_exact')
        AbstractFeature.set_description(self, "Proportion of aligned words with synonym lexical match and exact POS match")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        if len(alignments[0]) > 0:
            count = 0

            for index in alignments[0]:
                word_candidate = candidate_parsed[index[0] - 1]
                word_reference = reference_parsed[index[1] - 1]

                if wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Synonym' and wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Exact':
                    count += 1

            AbstractFeature.set_value(self, count / float(len(alignments[0])))
        else:
            AbstractFeature.set_value(self, 0)


class PropAlignedParaExact(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'prop_aligned_para_exact')
        AbstractFeature.set_description(self, "Proportion of aligned words with paraphrase lexical match and exact POS match")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        if len(alignments[0]) > 0:
            count = 0

            for index in alignments[0]:
                word_candidate = candidate_parsed[index[0] - 1]
                word_reference = reference_parsed[index[1] - 1]

                if wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Paraphrase' and wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Exact':
                    count += 1

            AbstractFeature.set_value(self, count / float(len(alignments[0])))
        else:
            AbstractFeature.set_value(self, 0)


class PropAlignedExactCoarse(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'prop_aligned_exact_coarse')
        AbstractFeature.set_description(self, "Proportion of aligned words with exact lexical match and coarse POS match")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        if len(alignments[0]) > 0:
            count = 0

            for index in alignments[0]:
                word_candidate = candidate_parsed[index[0] - 1]
                word_reference = reference_parsed[index[1] - 1]

                if wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Coarse':
                    count += 1

            AbstractFeature.set_value(self, count / float(len(alignments[0])))
        else:
            AbstractFeature.set_value(self, 0)


class PropAlignedSynCoarse(AbstractFeature):

    def __init__(self):
       AbstractFeature.__init__(self)
       AbstractFeature.set_name(self, 'prop_aligned_syn_coarse')
       AbstractFeature.set_description(self, "Proportion of aligned words with synonym lexical match and coarse POS match")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        if len(alignments[0]) > 0:
            count = 0

            for index in alignments[0]:
                word_candidate = candidate_parsed[index[0] - 1]
                word_reference = reference_parsed[index[1] - 1]

                if wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Coarse' and wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Synonym':
                    count += 1

            AbstractFeature.set_value(self, count / float(len(alignments[0])))
        else:
            AbstractFeature.set_value(self, 0)


class PropAlignedParaCoarse(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'prop_aligned_para_coarse')
        AbstractFeature.set_description(self, "Proportion of aligned words with paraphrase lexical match and coarse POS match")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        if len(alignments[0]) > 0:
            count = 0

            for index in alignments[0]:
                word_candidate = candidate_parsed[index[0] - 1]
                word_reference = reference_parsed[index[1] - 1]

                if wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Paraphrase' and wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Coarse':
                    count += 1

            AbstractFeature.set_value(self, count / float(len(alignments[0])))
        else:
            AbstractFeature.set_value(self, 0)


class PropAlignedSynDiff(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'prop_aligned_syn_diff')
        AbstractFeature.set_description(self, "Proportion of aligned words with synonym lexical match and different POS")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        if len(alignments[0]) > 0:
            count = 0

            for index in alignments[0]:
                word_candidate = candidate_parsed[index[0] - 1]
                word_reference = reference_parsed[index[1] - 1]

                if wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Synonym' and wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'None':
                    count += 1

            AbstractFeature.set_value(self, count / float(len(alignments[0])))
        else:
            AbstractFeature.set_value(self, 0)


class PropAlignedParaDiff(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'prop_aligned_para_diff')
        AbstractFeature.set_description(self, "Proportion of aligned words with paraphrase lexical match and different POS")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        if len(alignments[0]):
            count = 0

            for index in alignments[0]:
                word_candidate = candidate_parsed[index[0] - 1]
                word_reference = reference_parsed[index[1] - 1]

                if wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Paraphrase' and wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'None':
                    count += 1

            AbstractFeature.set_value(self, count / float(len(alignments[0])))
        else:
            AbstractFeature.set_value(self, 0)


class PropAlignedDistribExact(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'prop_aligned_distrib_exact')
        AbstractFeature.set_description(self, "Proportion of aligned words with distributional similarity and exact POS match")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        if len(alignments[0]) > 0:
            count = 0

            for index in alignments[0]:
                word_candidate = candidate_parsed[index[0] - 1]
                word_reference = reference_parsed[index[1] - 1]

                if wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Distributional' and wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Exact':
                    count += 1

            AbstractFeature.set_value(self, count / float(len(alignments[0])))
        else:
            AbstractFeature.set_value(self, 0)


class PropAlignedDistribCoarse(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'prop_aligned_distrib_coarse')
        AbstractFeature.set_description(self, "Proportion of aligned words with distributional similarity and coarse POS match")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        if len(alignments[0]) > 0:
            count = 0

            for index in alignments[0]:
                word_candidate = candidate_parsed[index[0] - 1]
                word_reference = reference_parsed[index[1] - 1]

                if wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Coarse' and wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Distributional':
                    count += 1

            AbstractFeature.set_value(self, count / float(len(alignments[0])))
        else:
            AbstractFeature.set_value(self, 0)


class PropAlignedDistribDiff(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'prop_aligned_distrib_diff')
        AbstractFeature.set_description(self, "Proportion of aligned words with distributional similarity and different POS")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        if len(alignments[0]):
            count = 0

            for index in alignments[0]:
                word_candidate = candidate_parsed[index[0] - 1]
                word_reference = reference_parsed[index[1] - 1]

                if wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'None' and wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Distributional':
                    count += 1

            AbstractFeature.set_value(self, count / float(len(alignments[0])))
        else:
            AbstractFeature.set_value(self, 0)


class AvgPenExactTest(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'avg_pen_exact_test')
        AbstractFeature.set_description(self, "Average CP for aligned words with exact match in the candidate (considered only for the words with CP > 0)")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        my_scorer = scorer.Scorer()
        difference = 0.0
        context = 0.0
        penalties = []

        if len(alignments[0]) == 0:
            AbstractFeature.set_value(self, 0)
            return

        for i, index in enumerate(alignments[0]):

            word_candidate = candidate_parsed[index[0] - 1]
            word_reference = reference_parsed[index[1] - 1]

            if wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'None':

                for dep_label in alignments[2][i]['srcDiff']:
                    if not dep_label.split('_')[0] in my_scorer.noisy_types:
                        difference += 1

                for dep_label in alignments[2][i]['srcCon']:
                    if not dep_label.split('_')[0] in my_scorer.noisy_types:
                        context += 1

                penalty = 0.0
                if context != 0:
                    penalty = difference / context * math.log(context + 1.0)

                if penalty > 0:
                    penalties.append(penalty)

        if len(penalties) > 0:
            AbstractFeature.set_value(self, numpy.mean(penalties))
        else:
            AbstractFeature.set_value(self, 0)

class AvgPenExactRef(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'avg_pen_exact_ref')
        AbstractFeature.set_description(self, "Average CP for aligned words with exact match in the reference (considered only for the words with CP > 0)")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        my_scorer = scorer.Scorer()
        difference = 0.0
        context = 0.0
        penalties = []

        if len(alignments[0]) == 0:
            AbstractFeature.set_value(self, 0)
            return

        for i, index in enumerate(alignments[0]):

            word_candidate = candidate_parsed[index[0] - 1]
            word_reference = reference_parsed[index[1] - 1]

            if wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'None':

                for dep_label in alignments[2][i]['tgtDiff']:
                    if not dep_label.split('_')[0] in my_scorer.noisy_types:
                        difference += 1

                for dep_label in alignments[2][i]['tgtCon']:
                    if not dep_label.split('_')[0] in my_scorer.noisy_types:
                        context += 1

                penalty = 0.0
                if context != 0:
                    penalty = difference / context * math.log(context + 1.0)

                if penalty > 0:
                    penalties.append(penalty)

        if len(penalties) > 0:
            AbstractFeature.set_value(self, numpy.mean(penalties))
        else:
            AbstractFeature.set_value(self, 0)


class AvgPenNoExactTest(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'avg_pen_no_exact_test')
        AbstractFeature.set_description(self, "Average CP for aligned words with non-exact match in the candidate (considered only for the words with CP > 0)")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        my_scorer = scorer.Scorer()
        difference = 0.0
        context = 0.0
        penalties = []

        if len(alignments[0]) == 0:
            AbstractFeature.set_value(self, 0)
            return

        for i, index in enumerate(alignments[0]):

            word_candidate = candidate_parsed[index[0] - 1]
            word_reference = reference_parsed[index[1] - 1]

            if not wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Exact':

                for dep_label in alignments[2][i]['srcDiff']:
                    if not dep_label.split('_')[0] in my_scorer.noisy_types:
                        difference += 1

                for dep_label in alignments[2][i]['srcCon']:
                    if not dep_label.split('_')[0] in my_scorer.noisy_types:
                        context += 1

                penalty = 0.0
                if context != 0:
                    penalty = difference / context * math.log(context + 1.0)

                if penalty > 0:
                    penalties.append(penalty)

        if len(penalties) > 0:
            AbstractFeature.set_value(self, numpy.mean(penalties))
        else:
            AbstractFeature.set_value(self, 0)

class AvgPenNoExactRef(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'avg_pen_no_exact_ref')
        AbstractFeature.set_description(self, "Average CP for aligned words with non-exact match in the reference (considered only for the words with CP > 0)")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        my_scorer = scorer.Scorer()
        difference = 0.0
        context = 0.0
        penalties = []

        if len(alignments[0]) == 0:
            AbstractFeature.set_value(self, 0)
            return

        for i, index in enumerate(alignments[0]):

            word_candidate = candidate_parsed[index[0] - 1]
            word_reference = reference_parsed[index[1] - 1]

            if not wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Exact':

                for dep_label in alignments[2][i]['tgtDiff']:
                    if not dep_label.split('_')[0] in my_scorer.noisy_types:
                        difference += 1

                for dep_label in alignments[2][i]['tgtCon']:
                    if not dep_label.split('_')[0] in my_scorer.noisy_types:
                        context += 1

                penalty = 0.0
                if context != 0:
                    penalty = difference / context * math.log(context + 1.0)

                if penalty > 0:
                    penalties.append(penalty)

        if len(penalties) > 0:
            AbstractFeature.set_value(self, numpy.mean(penalties))
        else:
            AbstractFeature.set_value(self, 0)


class PropExactPenTest(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'prop_exact_pen_test')
        AbstractFeature.set_description(self, "Proportion of exact matching words with CP in the candidate")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        if len(alignments[0]) == 0:
            AbstractFeature.set_value(self, 0)
            return

        counter_penalties = 0.0
        counter_words = 0.0

        for i, index in enumerate(alignments[0]):

            word_candidate = candidate_parsed[index[0] - 1]
            word_reference = reference_parsed[index[1] - 1]

            if wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'None':

                counter_words += 1

                if len(alignments[2][i]['srcDiff']):
                    counter_penalties += 1

        if counter_words > 0:
             AbstractFeature.set_value(self, counter_penalties / counter_words)
        else:
             AbstractFeature.set_value(self, 0.0)


class PropExactPenRef(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'prop_exact_pen_ref')
        AbstractFeature.set_description(self, "Proportion of exact matching words with CP in the reference")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        if len(alignments[0]) == 0:
            AbstractFeature.set_value(self, 0)
            return

        counter_penalties = 0.0
        counter_words = 0.0

        for i, index in enumerate(alignments[0]):

            word_candidate = candidate_parsed[index[0] - 1]
            word_reference = reference_parsed[index[1] - 1]

            if wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'None':

                counter_words += 1

                if len(alignments[2][i]['tgtDiff']):
                    counter_penalties += 1

        if counter_words > 0:
             AbstractFeature.set_value(self, counter_penalties / counter_words)
        else:
             AbstractFeature.set_value(self, 0.0)


class PropNoExactPenTest(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'prop_no_exact_pen_test')
        AbstractFeature.set_description(self, "Proportion of non-exact matching words with CP in the candidate")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        if len(alignments[0]) == 0:
            AbstractFeature.set_value(self, 0)
            return

        counter_penalties = 0.0
        counter_words = 0.0

        for i, index in enumerate(alignments[0]):

            word_candidate = candidate_parsed[index[0] - 1]
            word_reference = reference_parsed[index[1] - 1]

            if not wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Exact':

                counter_words += 1

                if len(alignments[2][i]['srcDiff']):
                    counter_penalties += 1

        if counter_words > 0:
            AbstractFeature.set_value(self, counter_penalties / counter_words)
        else:
            AbstractFeature.set_value(self, 0)


class PropNoExactPenRef(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'prop_no_exact_pen_ref')
        AbstractFeature.set_description(self, "Proportion of non-exact matching words with CP in the reference")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        if len(alignments[0]) == 0:
            AbstractFeature.set_value(self, 0)
            return

        counter_penalties = 0.0
        counter_words = 0.0

        for i, index in enumerate(alignments[0]):

            word_candidate = candidate_parsed[index[0] - 1]
            word_reference = reference_parsed[index[1] - 1]

            if not wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Exact':

                counter_words += 1

                if len(alignments[2][i]['tgtDiff']):
                     counter_penalties += 1

        if counter_words > 0:
            AbstractFeature.set_value(self, counter_penalties / counter_words)
        else:
            AbstractFeature.set_value(self, 0.0)


class PropContentPenTest(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'prop_content_pen_test')
        AbstractFeature.set_description(self, "Proportion of content words with CP in the candidate")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        if len(alignments[0]) == 0:
            AbstractFeature.set_value(self, 0)
            return

        counter_penalties = 0.0
        counter_words = 0.0

        for i, index in enumerate(alignments[0]):

            word_candidate = candidate_parsed[index[0] - 1]
            word_reference = reference_parsed[index[1] - 1]

            if not wordSim.functionWord(word_candidate.form):

                counter_words += 1

                if len(alignments[2][i]['srcDiff']):
                     counter_penalties += 1

        if counter_words > 0:
            AbstractFeature.set_value(self, counter_penalties / counter_words)
        else:
            AbstractFeature.set_value(self, 0)


class PropContentPenRef(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'prop_content_pen_ref')
        AbstractFeature.set_description(self, "Proportion of content words with CP in the reference")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        if len(alignments[0]) == 0:
            AbstractFeature.set_value(self, 0)
            return

        counter_penalties = 0.0
        counter_words = 0.0

        for i, index in enumerate(alignments[0]):

            word_candidate = candidate_parsed[index[0] - 1]
            word_reference = reference_parsed[index[1] - 1]

            if not wordSim.functionWord(word_candidate.form):

                counter_words += 1

                if len(alignments[2][i]['tgtDiff']):
                    counter_penalties += 1

        if counter_words > 0:
            AbstractFeature.set_value(self, counter_penalties / counter_words)
        else:
            AbstractFeature.set_value(self, 0)

class PropFunctionPenTest(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'prop_function_pen_test')
        AbstractFeature.set_description(self, "Proportion of function words with CP in the candidate")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        if len(alignments[0]) == 0:
            AbstractFeature.set_value(self, 0)
            return

        counter_penalties = 0.0
        counter_words = 0.0

        for i, index in enumerate(alignments[0]):

            word_candidate = candidate_parsed[index[0] - 1]
            word_reference = reference_parsed[index[1] - 1]

            if wordSim.functionWord(word_candidate.form):

                counter_words += 1

                if len(alignments[2][i]['srcDiff']):
                    counter_penalties += 1

        if counter_words > 0:
            AbstractFeature.set_value(self, counter_penalties / counter_words)
        else:
            AbstractFeature.set_value(self, 0.0)

class PropFunctionPenRef(AbstractFeature):

    def __init__(self):
        AbstractFeature.__init__(self)
        AbstractFeature.set_name(self, 'prop_function_pen_ref')
        AbstractFeature.set_description(self, "Proportion of function words with CP in the reference")

    def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

        if len(alignments[0]) == 0:
            AbstractFeature.set_value(self, 0)
            return

        counter_penalties = 0.0
        counter_words = 0.0

        for i, index in enumerate(alignments[0]):

            word_candidate = candidate_parsed[index[0] - 1]
            word_reference = reference_parsed[index[1] - 1]

            if wordSim.functionWord(word_reference.form):

                counter_words += 1

                if len(alignments[2][i]['tgtDiff']):
                    counter_penalties += 1

        if counter_words > 0:
            AbstractFeature.set_value(self, counter_penalties / counter_words)
        else:
            AbstractFeature.set_value(self, 0.0)
