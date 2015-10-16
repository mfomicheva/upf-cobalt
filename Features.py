__author__ = 'u88591'

import wordSim
import config
import scorer
import math
import numpy

class Abstract(object):

    def __init__(self):
        self.computable = bool
        self.value = float
        self.index = str
        self.description = str


    def getValue(self):
        return self.value

    def setValue(self, value):
        self.value = value

    def setDescription(self, d):
        self.description = d

    def getDescription(self):
        return self.description


    def getIndex(self):
        return self.index

    def setIndex(self, index):
        self.index = index


class Feature001(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '001')
        Abstract.setDescription(self, "Number of words in the candidate")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):
         Abstract.setValue(self, len(candidate_parsed))

class Feature002(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '002')
        Abstract.setDescription(self, "Number of words in the reference")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):
         Abstract.setValue(self, len(reference_parsed))


class Feature003(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '003')
        Abstract.setDescription(self, "Number of content words in the candidate")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):
         count = 0
         for word in candidate_parsed:
             if not wordSim.functionWord(word.form):
                 count += 1

         Abstract.setValue(self, count)

class Feature004(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '004')
        Abstract.setDescription(self, "Number of content words in the reference")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):
         count = 0
         for word in reference_parsed:
             if not wordSim.functionWord(word.form):
                 count += 1

         Abstract.setValue(self, count)

class Feature005(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '005')
        Abstract.setDescription(self, "Number of function words in the candidate")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):
         count = 0
         for word in candidate_parsed:
             if wordSim.functionWord(word.form):
                 count += 1

         Abstract.setValue(self, count)

class Feature006(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '006')
        Abstract.setDescription(self, "Number of function words in the reference")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):
         count = 0
         for word in reference_parsed:
             if wordSim.functionWord(word.form):
                 count += 1

         Abstract.setValue(self, count)

class Feature007(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '007')
        Abstract.setDescription(self, "Number of aligned words")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):
         Abstract.setValue(self, len(alignments[0]))

class Feature008(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '008')
        Abstract.setDescription(self, "Proportion of aligned words in the candidate")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):
         Abstract.setValue(self, len(alignments[0]) / float(len(candidate_parsed)))

class Feature009(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '009')
        Abstract.setDescription(self, "Proportion of aligned words in the reference")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):
         Abstract.setValue(self, len(alignments[0]) / float(len(reference_parsed)))

class Feature010(Abstract):

    ## Supposing content words can only be aligned to content words

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '010')
        Abstract.setDescription(self, "Proportion of aligned content words")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         count = 0
         for word in alignments[1]:
             if word[0] not in config.stopwords and word[0] not in config.punctuations:
                 count += 1

         Abstract.setValue(self, count / float(len(alignments[0])))

class Feature011(Abstract):

    ## Supposing content words can only be aligned to content words

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '011')
        Abstract.setDescription(self, "Proportion of aligned function words")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         count = 0
         for word in alignments[1]:
             if word[0] in config.stopwords or word[0] in config.punctuations:
                 count += 1

         Abstract.setValue(self, count / float(len(alignments[0])))

class Feature012(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '012')
        Abstract.setDescription(self, "Proportion of aligned words with exact lexical match and exact POS match")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         count = 0

         for index in alignments[0]:
             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Exact' and wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact':
                 count += 1

         Abstract.setValue(self, count / float(len(alignments[0])))

class Feature013(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '013')
        Abstract.setDescription(self, "Proportion of aligned words with synonym lexical match and exact POS match")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         count = 0

         for index in alignments[0]:
             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Exact' and wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Synonym':
                 count += 1

         Abstract.setValue(self, count / float(len(alignments[0])))

class Feature014(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '014')
        Abstract.setDescription(self, "Proportion of aligned words with paraphrase lexical match and exact POS match")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         count = 0

         for index in alignments[0]:
             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Exact' and wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Paraphrase':
                 count += 1

         Abstract.setValue(self, count / float(len(alignments[0])))

class Feature015(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '015')
        Abstract.setDescription(self, "Proportion of aligned words with exact lexical match and coarse POS match")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         count = 0

         for index in alignments[0]:
             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Coarse' and wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact':
                 count += 1

         Abstract.setValue(self, count / float(len(alignments[0])))

class Feature016(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '016')
        Abstract.setDescription(self, "Proportion of aligned words with synonym lexical match and coarse POS match")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         count = 0

         for index in alignments[0]:
             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Coarse' and wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Synonym':
                 count += 1

         Abstract.setValue(self, count / float(len(alignments[0])))

class Feature017(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '017')
        Abstract.setDescription(self, "Proportion of aligned words with paraphrase lexical match and coarse POS match")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         count = 0

         for index in alignments[0]:
             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Coarse' and wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Paraphrase':
                 count += 1

         Abstract.setValue(self, count / float(len(alignments[0])))

class Feature018(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '018')
        Abstract.setDescription(self, "Proportion of aligned words with synonym lexical match and different POS")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         count = 0

         for index in alignments[0]:
             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'None' and wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Synonym':
                 count += 1

         Abstract.setValue(self, count / float(len(alignments[0])))

class Feature019(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '019')
        Abstract.setDescription(self, "Proportion of aligned words with paraphrase lexical match and different POS")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         count = 0

         for index in alignments[0]:
             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'None' and wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Paraphrase':
                 count += 1

         Abstract.setValue(self, count / float(len(alignments[0])))


class Feature020(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '020')
        Abstract.setDescription(self, "Average CP(group 1) for aligned words with exact match in the candidate")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         my_scorer = scorer.Scorer()
         difference = 0.0
         context = 0.0

         for i, index in enumerate(alignments[0]):

             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'None':

                 for dep_label in alignments[2][i]['srcDiff']:
                     if dep_label.split('_')[0] in my_scorer.argument_types or dep_label.split('_')[0] in my_scorer.modifier_types:
                         difference += 1

                 for dep_label in alignments[2][i]['srcCon']:
                     if dep_label.split('_')[0] in my_scorer.argument_types or dep_label.split('_')[0] in my_scorer.modifier_types:
                         context += 1

         result = 0.0
         if context != 0:
             result = difference / context

         Abstract.setValue(self, result)

class Feature021(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '021')
        Abstract.setDescription(self, "Average CP(group 1) for aligned words with exact match in the reference")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         my_scorer = scorer.Scorer()
         difference = 0.0
         context = 0.0

         for i, index in enumerate(alignments[0]):

             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'None':

                 for dep_label in alignments[2][i]['tgtDiff']:
                     if dep_label.split('_')[0] in my_scorer.argument_types or dep_label.split('_')[0] in my_scorer.modifier_types:
                         difference += 1

                 for dep_label in alignments[2][i]['tgtCon']:
                     if dep_label.split('_')[0] in my_scorer.argument_types or dep_label.split('_')[0] in my_scorer.modifier_types:
                         context += 1

         result = 0.0
         if context != 0:
             result = difference / context

         Abstract.setValue(self, result)


class Feature022(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '022')
        Abstract.setDescription(self, "Average CP(group 2) for aligned words with exact match in the candidate")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         my_scorer = scorer.Scorer()
         difference = 0.0
         context = 0.0

         for i, index in enumerate(alignments[0]):

             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'None':

                 for dep_label in alignments[2][i]['srcDiff']:
                     if dep_label.split('_')[0] not in my_scorer.argument_types and not dep_label.split('_')[0] in my_scorer.modifier_types:
                         difference += 1

                 for dep_label in alignments[2][i]['srcCon']:
                     if not dep_label.split('_')[0] in my_scorer.argument_types and not dep_label.split('_')[0] in my_scorer.modifier_types:
                         context += 1

         result = 0.0
         if context != 0:
             result = difference / context

         Abstract.setValue(self, result)

class Feature023(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '023')
        Abstract.setDescription(self, "Average CP(group 2) for aligned words with exact match in the reference")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         my_scorer = scorer.Scorer()
         difference = 0.0
         context = 0.0

         for i, index in enumerate(alignments[0]):

             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'None':

                 for dep_label in alignments[2][i]['tgtDiff']:
                     if not dep_label.split('_')[0] in my_scorer.argument_types and not dep_label.split('_')[0] in my_scorer.modifier_types:
                         difference += 1

                 for dep_label in alignments[2][i]['tgtCon']:
                     if not dep_label.split('_')[0] in my_scorer.argument_types and not dep_label.split('_')[0] in my_scorer.modifier_types:
                         context += 1

         result = 0.0
         if context != 0:
             result = difference / context

         Abstract.setValue(self, result)


class Feature024(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '024')
        Abstract.setDescription(self, "Average CP(group 1) for aligned words with non-exact match in the candidate")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         my_scorer = scorer.Scorer()
         difference = 0.0
         context = 0.0

         for i, index in enumerate(alignments[0]):

             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if not wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Exact':

                 for dep_label in alignments[2][i]['srcDiff']:
                     if dep_label.split('_')[0] in my_scorer.argument_types or dep_label.split('_')[0] in my_scorer.modifier_types:
                         difference += 1

                 for dep_label in alignments[2][i]['srcCon']:
                     if dep_label.split('_')[0] in my_scorer.argument_types or dep_label.split('_')[0] in my_scorer.modifier_types:
                         context += 1

         result = 0.0
         if context != 0:
             result = difference / context

         Abstract.setValue(self, result)

class Feature025(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '025')
        Abstract.setDescription(self, "Average CP(group 1) for aligned words with non-exact match in the reference")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         my_scorer = scorer.Scorer()
         difference = 0.0
         context = 0.0

         for i, index in enumerate(alignments[0]):

             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if not wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Exact':

                 for dep_label in alignments[2][i]['tgtDiff']:
                     if dep_label.split('_')[0] in my_scorer.argument_types or dep_label.split('_')[0] in my_scorer.modifier_types:
                         difference += 1

                 for dep_label in alignments[2][i]['tgtCon']:
                     if dep_label.split('_')[0] in my_scorer.argument_types or dep_label.split('_')[0] in my_scorer.modifier_types:
                         context += 1

         result = 0.0
         if context != 0:
             result = difference / context

         Abstract.setValue(self, result)


class Feature026(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '026')
        Abstract.setDescription(self, "Average CP(group 2) for aligned words with non-exact match in the candidate")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         my_scorer = scorer.Scorer()
         difference = 0.0
         context = 0.0

         for i, index in enumerate(alignments[0]):

             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if not wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Exact':

                 for dep_label in alignments[2][i]['srcDiff']:
                     if dep_label.split('_')[0] not in my_scorer.argument_types and not dep_label.split('_')[0] in my_scorer.modifier_types:
                         difference += 1

                 for dep_label in alignments[2][i]['srcCon']:
                     if not dep_label.split('_')[0] in my_scorer.argument_types and not dep_label.split('_')[0] in my_scorer.modifier_types:
                         context += 1

         result = 0.0
         if context != 0:
             result = difference / context

         Abstract.setValue(self, result)

class Feature027(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '027')
        Abstract.setDescription(self, "Average CP(group 2) for aligned words with non-exact match in the reference")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         my_scorer = scorer.Scorer()
         difference = 0.0
         context = 0.0

         for i, index in enumerate(alignments[0]):

             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if not wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Exact':

                 for dep_label in alignments[2][i]['tgtDiff']:
                     if not dep_label.split('_')[0] in my_scorer.argument_types and not dep_label.split('_')[0] in my_scorer.modifier_types:
                         difference += 1

                 for dep_label in alignments[2][i]['tgtCon']:
                     if not dep_label.split('_')[0] in my_scorer.argument_types and not dep_label.split('_')[0] in my_scorer.modifier_types:
                         context += 1

         result = 0.0
         if context != 0:
             result = difference / context

         Abstract.setValue(self, result)

class Feature028(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '028')
        Abstract.setDescription(self, "Maximum CP(group 1) for aligned words with exact match in the candidate")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         my_scorer = scorer.Scorer()
         penalties = []

         for i, index in enumerate(alignments[0]):

             difference = 0.0
             context = 0.0

             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'None':

                 for dep_label in alignments[2][i]['srcDiff']:
                     if dep_label.split('_')[0] in my_scorer.argument_types or dep_label.split('_')[0] in my_scorer.modifier_types:
                         difference += 1

                 for dep_label in alignments[2][i]['srcCon']:
                     if dep_label.split('_')[0] in my_scorer.argument_types or dep_label.split('_')[0] in my_scorer.modifier_types:
                         context += 1

                 if context > 0:
                     penalties.append(difference / context)
                 else:
                     penalties.append(0.0)

         if len(penalties) > 0:
             Abstract.setValue(self, max(penalties))
         else:
            Abstract.setValue(self, 0.0)

class Feature029(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '029')
        Abstract.setDescription(self, "Maximum CP(group 1) for aligned words with exact match in the reference")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         my_scorer = scorer.Scorer()
         penalties = []

         for i, index in enumerate(alignments[0]):

             difference = 0.0
             context = 0.0

             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'None':

                 for dep_label in alignments[2][i]['tgtDiff']:
                     if dep_label.split('_')[0] in my_scorer.argument_types or dep_label.split('_')[0] in my_scorer.modifier_types:
                         difference += 1

                 for dep_label in alignments[2][i]['tgtCon']:
                     if dep_label.split('_')[0] in my_scorer.argument_types or dep_label.split('_')[0] in my_scorer.modifier_types:
                         context += 1

                 if context > 0:
                     penalties.append(difference / context)
                 else:
                     penalties.append(0.0)

         if len(penalties) > 0:
             Abstract.setValue(self, max(penalties))
         else:
            Abstract.setValue(self, 0.0)


class Feature030(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '030')
        Abstract.setDescription(self, "Maximum CP(group 2) for aligned words with exact match in the candidate")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         my_scorer = scorer.Scorer()
         penalties = []

         for i, index in enumerate(alignments[0]):

             difference = 0.0
             context = 0.0

             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'None':

                 for dep_label in alignments[2][i]['srcDiff']:
                     if dep_label.split('_')[0] not in my_scorer.argument_types and not dep_label.split('_')[0] in my_scorer.modifier_types:
                         difference += 1

                 for dep_label in alignments[2][i]['srcCon']:
                     if not dep_label.split('_')[0] in my_scorer.argument_types and not dep_label.split('_')[0] in my_scorer.modifier_types:
                         context += 1

                 if context > 0:
                     penalties.append(difference / context)
                 else:
                     penalties.append(0.0)

         if len(penalties) > 0:
             Abstract.setValue(self, max(penalties))
         else:
            Abstract.setValue(self, 0.0)


class Feature031(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '031')
        Abstract.setDescription(self, "Maximum CP(group 2) for aligned words with exact match in the reference")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         my_scorer = scorer.Scorer()
         penalties = []

         for i, index in enumerate(alignments[0]):

             difference = 0.0
             context = 0.0

             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'None':

                 for dep_label in alignments[2][i]['tgtDiff']:
                     if not dep_label.split('_')[0] in my_scorer.argument_types and not dep_label.split('_')[0] in my_scorer.modifier_types:
                         difference += 1

                 for dep_label in alignments[2][i]['tgtCon']:
                     if not dep_label.split('_')[0] in my_scorer.argument_types and not dep_label.split('_')[0] in my_scorer.modifier_types:
                         context += 1

             if context > 0:
                 penalties.append(difference / context)
             else:
                 penalties.append(0.0)

         if len(penalties) > 0:
             Abstract.setValue(self, max(penalties))
         else:
            Abstract.setValue(self, 0.0)


class Feature032(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '032')
        Abstract.setDescription(self, "Maximum CP(group 1) for aligned words with non-exact match in the candidate")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         my_scorer = scorer.Scorer()
         penalties = []

         for i, index in enumerate(alignments[0]):

             difference = 0.0
             context = 0.0

             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if not wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Exact':

                 for dep_label in alignments[2][i]['srcDiff']:
                     if dep_label.split('_')[0] in my_scorer.argument_types or dep_label.split('_')[0] in my_scorer.modifier_types:
                         difference += 1

                 for dep_label in alignments[2][i]['srcCon']:
                     if dep_label.split('_')[0] in my_scorer.argument_types or dep_label.split('_')[0] in my_scorer.modifier_types:
                         context += 1

             if context > 0:
                 penalties.append(difference / context)
             else:
                 penalties.append(0.0)

         if len(penalties) > 0:
             Abstract.setValue(self, max(penalties))
         else:
            Abstract.setValue(self, 0.0)

class Feature033(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '033')
        Abstract.setDescription(self, "Maximum CP(group 1) for aligned words with non-exact match in the reference")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         my_scorer = scorer.Scorer()
         penalties = []

         for i, index in enumerate(alignments[0]):

             difference = 0.0
             context = 0.0

             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if not wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Exact':

                 for dep_label in alignments[2][i]['tgtDiff']:
                     if dep_label.split('_')[0] in my_scorer.argument_types or dep_label.split('_')[0] in my_scorer.modifier_types:
                         difference += 1

                 for dep_label in alignments[2][i]['tgtCon']:
                     if dep_label.split('_')[0] in my_scorer.argument_types or dep_label.split('_')[0] in my_scorer.modifier_types:
                         context += 1

             if context > 0:
                 penalties.append(difference / context)
             else:
                 penalties.append(0.0)

         if len(penalties) > 0:
             Abstract.setValue(self, max(penalties))
         else:
            Abstract.setValue(self, 0.0)


class Feature034(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '034')
        Abstract.setDescription(self, "Maximum CP(group 2) for aligned words with non-exact match in the candidate")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         my_scorer = scorer.Scorer()
         penalties = []

         for i, index in enumerate(alignments[0]):

             difference = 0.0
             context = 0.0

             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if not wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Exact':

                 for dep_label in alignments[2][i]['srcDiff']:
                     if dep_label.split('_')[0] not in my_scorer.argument_types and not dep_label.split('_')[0] in my_scorer.modifier_types:
                         difference += 1

                 for dep_label in alignments[2][i]['srcCon']:
                     if not dep_label.split('_')[0] in my_scorer.argument_types and not dep_label.split('_')[0] in my_scorer.modifier_types:
                         context += 1

             if context > 0:
                 penalties.append(difference / context)
             else:
                 penalties.append(0.0)

         if len(penalties) > 0:
             Abstract.setValue(self, max(penalties))
         else:
            Abstract.setValue(self, 0.0)

class Feature035(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '035')
        Abstract.setDescription(self, "Maximum CP(group 2) for aligned words with non-exact match in the reference")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         my_scorer = scorer.Scorer()
         penalties = []

         for i, index in enumerate(alignments[0]):

             difference = 0.0
             context = 0.0

             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if not wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Exact' and not wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Exact':

                 for dep_label in alignments[2][i]['tgtDiff']:
                     if not dep_label.split('_')[0] in my_scorer.argument_types and not dep_label.split('_')[0] in my_scorer.modifier_types:
                         difference += 1

                 for dep_label in alignments[2][i]['tgtCon']:
                     if not dep_label.split('_')[0] in my_scorer.argument_types and not dep_label.split('_')[0] in my_scorer.modifier_types:
                         context += 1

                 if context > 0:
                     penalties.append(difference / context)
                 else:
                     penalties.append(0.0)

         if len(penalties) > 0:
             Abstract.setValue(self, max(penalties))
         else:
            Abstract.setValue(self, 0.0)


class Feature036(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '036')
        Abstract.setDescription(self, "Proportion of exact matching words with CP in the candidate")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

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
             Abstract.setValue(self, counter_penalties / counter_words)
         else:
             Abstract.setValue(self, 0.0)


class Feature037(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '037')
        Abstract.setDescription(self, "Proportion of exact matching words with CP in the reference")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

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
             Abstract.setValue(self, counter_penalties / counter_words)
         else:
             Abstract.setValue(self, 0.0)

class Feature038(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '038')
        Abstract.setDescription(self, "Proportion of non-exact matching words with CP in the candidate")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

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
             Abstract.setValue(self, counter_penalties / counter_words)
         else:
             Abstract.setValue(self, 0.0)


class Feature039(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '039')
        Abstract.setDescription(self, "Proportion of non-exact matching words with CP in the reference")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

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
             Abstract.setValue(self, counter_penalties / counter_words)
         else:
             Abstract.setValue(self, 0.0)


class Feature040(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '040')
        Abstract.setDescription(self, "Proportion of content words with CP in the candidate")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

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
             Abstract.setValue(self, counter_penalties / counter_words)
         else:
             Abstract.setValue(self, 0.0)

class Feature041(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '041')
        Abstract.setDescription(self, "Proportion of content words with CP in the reference")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

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
             Abstract.setValue(self, counter_penalties / counter_words)
         else:
             Abstract.setValue(self, 0.0)

class Feature042(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '042')
        Abstract.setDescription(self, "Proportion of function words with CP in the candidate")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

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
             Abstract.setValue(self, counter_penalties / counter_words)
         else:
             Abstract.setValue(self, 0.0)

class Feature043(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '043')
        Abstract.setDescription(self, "Proportion of function words with CP in the reference")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

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
             Abstract.setValue(self, counter_penalties / counter_words)
         else:
             Abstract.setValue(self, 0.0)

class Feature044(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '044')
        Abstract.setDescription(self, "Proportion of aligned words with distributional similarity and exact POS match")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         count = 0

         for index in alignments[0]:
             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Exact' and wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Distributional':
                 count += 1

         Abstract.setValue(self, count / float(len(alignments[0])))

class Feature045(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '045')
        Abstract.setDescription(self, "Proportion of aligned words with distributional similarity and coarse POS match")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         count = 0

         for index in alignments[0]:
             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'Coarse' and wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Distributional':
                 count += 1

         Abstract.setValue(self, count / float(len(alignments[0])))

class Feature046(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '046')
        Abstract.setDescription(self, "Proportion of aligned words with distributional similarity and different POS")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         count = 0

         for index in alignments[0]:
             word_candidate = candidate_parsed[index[0] - 1]
             word_reference = reference_parsed[index[1] - 1]

             if wordSim.comparePos(word_candidate.pos, word_reference.pos) == 'None' and wordSim.wordRelatednessFeature(word_candidate, word_reference) == 'Distributional':
                 count += 1

         Abstract.setValue(self, count / float(len(alignments[0])))


class Feature047(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '047')
        Abstract.setDescription(self, "Average CP for aligned words with exact match in the candidate (considered only for the words with CP > 0)")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         my_scorer = scorer.Scorer()
         difference = 0.0
         context = 0.0
         penalties = []

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
            Abstract.setValue(self, numpy.mean(penalties))

class Feature048(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '048')
        Abstract.setDescription(self, "Average CP for aligned words with exact match in the reference (considered only for the words with CP > 0)")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         my_scorer = scorer.Scorer()
         difference = 0.0
         context = 0.0
         penalties = []

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
            Abstract.setValue(self, numpy.mean(penalties))


class Feature049(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '049')
        Abstract.setDescription(self, "Average CP for aligned words with non-exact match in the candidate (considered only for the words with CP > 0)")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         my_scorer = scorer.Scorer()
         difference = 0.0
         context = 0.0
         penalties = []

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
            Abstract.setValue(self, numpy.mean(penalties))

class Feature050(Abstract):

     def __init__(self):
        Abstract.__init__(self)
        Abstract.setIndex(self, '050')
        Abstract.setDescription(self, "Average CP for aligned words with non-exact match in the reference (considered only for the words with CP > 0)")

     def run(self, candidate, reference, candidate_parsed, reference_parsed, alignments):

         my_scorer = scorer.Scorer()
         difference = 0.0
         context = 0.0
         penalties = []

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
            Abstract.setValue(self, numpy.mean(penalties))
