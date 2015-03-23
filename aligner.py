import math
from alignerConfig import AlignerConfig
from wordSim import *
from util import *
from coreNlpUtil import *


class Aligner(object):

    config = None

    scorer = None

    def __init__(self, language, scorer):
        self.config = AlignerConfig(language)
        self.scorer = scorer

    def is_similar(self, item1, item2, pos1, pos2, is_opposite, relation):
        result = False
        group = self.config.get_similar_group(pos1, pos2, is_opposite, relation)

        if is_opposite:
            for subgroup in group:
                if item1 in subgroup[0] and item2 in subgroup[1]:
                    result = True
        else:
            for subgroup in group:
                if item1 in subgroup and item2 in subgroup:
                    result = True
        return result

    def compareNodes(self, sourceNodes, targetNodes, pos, opposite, relationDirection, existingAlignments, sourcePosTags, targetPosTags, sourceLemmas, targetLemmas):
        # search for nodes in common or equivalent function

        relatedness = 0
        relativeAlignments = []
        weightedRelatedness = 0

        for ktem in sourceNodes:
            for ltem in targetNodes:
                if ((ktem[0], ltem[0]) in existingAlignments or max(wordRelatedness(ktem[1], sourcePosTags[ktem[0]-1], ltem[1], targetPosTags[ltem[0]-1], self.scorer), wordRelatedness(sourceLemmas[ktem[0]-1], sourcePosTags[ktem[0]-1], targetLemmas[ltem[0]-1], targetPosTags[ltem[0]-1], self.scorer)) >= self.config.similarity_threshold) and (
                    (ktem[2] == ltem[2]) or
                        ((relationDirection != 'child_parent') and (
                            self.is_similar(ktem[2], ltem[2], pos, 'noun', opposite, relationDirection) or
                            self.is_similar(ktem[2], ltem[2], pos, 'verb', opposite, relationDirection) or
                            self.is_similar(ktem[2], ltem[2], pos, 'adjective', opposite, relationDirection) or
                            self.is_similar(ktem[2], ltem[2], pos, 'adverb', opposite, relationDirection))) or
                        ((relationDirection == 'child_parent') and (
                            self.is_similar(ltem[2], ktem[2], pos, 'noun', opposite, relationDirection) or
                            self.is_similar(ltem[2], ktem[2], pos, 'verb', opposite, relationDirection) or
                            self.is_similar(ltem[2], ktem[2], pos, 'adjective', opposite, relationDirection) or
                            self.is_similar(ltem[2], ktem[2], pos, 'adverb', opposite, relationDirection)))):

                    # if ltem[2] == 'det' or ktem[2] == 'det':
                    #     #weightOnFunction = 0.0
                    #     weightOnFunction = 1.0
                    # else:
                    #     weightOnFunction = 1.0

                    relatedness += max(wordRelatedness(ktem[1], sourcePosTags[ktem[0]-1], ltem[1], targetPosTags[ltem[0]-1], self.scorer), wordRelatedness(sourceLemmas[ktem[0]-1], sourcePosTags[ktem[0]-1], targetLemmas[ltem[0]-1], targetPosTags[ltem[0]-1], self.scorer))
                    relativeAlignments.append([ktem[0], ltem[0]])
                    #weightedRelatedness +=max(wordRelatedness(ktem[1], sourcePosTags[ktem[0]-1], ltem[1], targetPosTags[ltem[0]-1], self.scorer), wordRelatedness(sourceLemmas[ktem[0]-1], sourcePosTags[ktem[0]-1], targetLemmas[ltem[0]-1], targetPosTags[ltem[0]-1], self.scorer)) * weightOnFunction



        #return [relatedness, relativeAlignments, weightedRelatedness]
        return [relatedness, relativeAlignments]


    def findDependencySimilarity(self, pos, source, sourceIndex, target, targetIndex, sourceDParse, targetDParse, existingAlignments, sourcePosTags, targetPosTags, sourceLemmas, targetLemmas):
        sourceWordParents = findParents(sourceDParse, sourceIndex, source)
        sourceWordChildren = findChildren(sourceDParse, sourceIndex, source)
        targetWordParents = findParents(targetDParse, targetIndex, target)
        targetWordChildren = findChildren(targetDParse, targetIndex, target)

        compareParents = self.compareNodes(sourceWordParents, targetWordParents, pos, False, 'parent', existingAlignments, sourcePosTags, targetPosTags, sourceLemmas, targetLemmas)
        compareChildren = self.compareNodes(sourceWordChildren, targetWordChildren, pos, False, 'child', existingAlignments, sourcePosTags, targetPosTags, sourceLemmas, targetLemmas)
        compareParentChildren = self.compareNodes(sourceWordParents, targetWordChildren, pos, True, 'parent_child', existingAlignments, sourcePosTags, targetPosTags, sourceLemmas, targetLemmas)
        compareChildrenParent = self.compareNodes(sourceWordParents, targetWordChildren, pos, True, 'child_parent', existingAlignments, sourcePosTags, targetPosTags, sourceLemmas, targetLemmas)

        relatedness = compareParents[0] + compareChildren[0] + compareParentChildren[0] + compareChildrenParent[0]
        relativeAlignments = compareParents[1] + compareChildren[1] + compareParentChildren[1] + compareChildrenParent[1]
        #weightedRelatedness = compareParents[2] + compareChildren[2] + compareParentChildren[2] + compareChildrenParent[2]

        #return [relatedness, relativeAlignments, weightedRelatedness]
        return [relatedness, relativeAlignments]


    ##############################################################################################################################
    def alignPos(self, pos, posCode, source, target, sourceParseResult, targetParseResult, existingAlignments):
    # source and target:: each is a list of elements of the form:
    # [[character begin offset, character end offset], word index, word, lemma, pos tag]

        global scorer
        global theta1

        posAlignments = []

        sourceWordIndices = [i+1 for i in xrange(len(source))]
        targetWordIndices = [i+1 for i in xrange(len(target))]

        sourceWordIndicesAlreadyAligned = sorted(list(set([item[0] for item in existingAlignments])))
        targetWordIndicesAlreadyAligned = sorted(list(set([item[1] for item in existingAlignments])))

        sourceWords = [item[2] for item in source]
        targetWords = [item[2] for item in target]

        sourceLemmas = [item[3] for item in source]
        targetLemmas = [item[3] for item in target]

        sourcePosTags = [item[4] for item in source]
        targetPosTags = [item[4] for item in target]

        sourceDParse = dependencyParseAndPutOffsets(sourceParseResult)
        targetDParse = dependencyParseAndPutOffsets(targetParseResult)


        numberOfPosWordsInSource = 0

        evidenceCountsMatrix = {}
        relativeAlignmentsMatrix = {}
        wordSimilarities = {}

        # construct the two matrices in the following loop
        for i in sourceWordIndices:
            if i in sourceWordIndicesAlreadyAligned or (sourcePosTags[i-1][0].lower() != posCode and sourcePosTags[i-1].lower() != 'prp'):
                continue

            numberOfPosWordsInSource += 1

            for j in targetWordIndices:
                if j in targetWordIndicesAlreadyAligned or (targetPosTags[j-1][0].lower() != posCode and targetPosTags[j-1].lower() != 'prp'):
                    continue

                if max(wordRelatedness(sourceWords[i-1], sourcePosTags[i-1], targetWords[j-1], targetPosTags[j-1], self.scorer), wordRelatedness(sourceLemmas[i-1], sourcePosTags[i-1], targetLemmas[j-1], targetPosTags[j-1], self.scorer)) < self.config.similarity_threshold:
                    continue

                wordSimilarities[(i, j)] = max(wordRelatedness(sourceWords[i-1], sourcePosTags[i-1], targetWords[j-1], targetPosTags[j-1], self.scorer), wordRelatedness(sourceLemmas[i-1], sourcePosTags[i-1], targetLemmas[j-1], targetPosTags[j-1], self.scorer))

                dependencySimilarity = self.findDependencySimilarity(pos, source, i, target, j, sourceDParse, targetDParse, existingAlignments + posAlignments, sourcePosTags, targetPosTags, sourceLemmas, targetLemmas)

                if dependencySimilarity[0] > self.config.similarity_threshold:
                    evidenceCountsMatrix[(i, j)] = dependencySimilarity[0]
                    relativeAlignmentsMatrix[(i, j)] = dependencySimilarity[1]

        # now use the collected stats to align
        for n in xrange(numberOfPosWordsInSource):

            maxEvidenceCountForCurrentPass = 0
            maxOverallValueForCurrentPass = 0
            indexPairWithStrongestTieForCurrentPass = [-1, -1]

            for i in sourceWordIndices:
                if i in sourceWordIndicesAlreadyAligned or sourcePosTags[i-1][0].lower() != posCode or sourceLemmas[i-1] in stopwords:
                    continue

                for j in targetWordIndices:
                    if j in targetWordIndicesAlreadyAligned or targetPosTags[j-1][0].lower() != posCode or targetLemmas[j-1] in stopwords:
                        continue

                    if (i, j) in evidenceCountsMatrix and theta1*wordSimilarities[(i, j)]+(1-theta1)*evidenceCountsMatrix[(i, j)]>maxOverallValueForCurrentPass:
                        maxOverallValueForCurrentPass = theta1*wordSimilarities[(i, j)]+(1-theta1)*evidenceCountsMatrix[(i, j)]
                        maxEvidenceCountForCurrentPass = evidenceCountsMatrix[(i, j)]
                        indexPairWithStrongestTieForCurrentPass = [i, j]

            if maxEvidenceCountForCurrentPass > 0:
                posAlignments.append(indexPairWithStrongestTieForCurrentPass)
                sourceWordIndicesAlreadyAligned.append(indexPairWithStrongestTieForCurrentPass[0])
                targetWordIndicesAlreadyAligned.append(indexPairWithStrongestTieForCurrentPass[1])
                for item in relativeAlignmentsMatrix[(indexPairWithStrongestTieForCurrentPass[0], indexPairWithStrongestTieForCurrentPass[1])]:
                    if item[0] != 0 and item[1] != 0 and item[0] not in sourceWordIndicesAlreadyAligned and item[1] not in targetWordIndicesAlreadyAligned:
                        posAlignments.append(item)
                        sourceWordIndicesAlreadyAligned.append(item[0])
                        targetWordIndicesAlreadyAligned.append(item[1])
            else:
                break

        return posAlignments


    ##############################################################################################################################
    def alignNamedEntities(self, source, target, sourceParseResult, targetParseResult, existingAlignments):
    # source and target:: each is a list of elements of the form:
    # [[character begin offset, character end offset], word index, word, lemma, pos tag]

        global punctuations

        alignments = []

        sourceNamedEntities = ner(sourceParseResult)
        sourceNamedEntities = sorted(sourceNamedEntities, key=len)

        targetNamedEntities = ner(targetParseResult)
        targetNamedEntities = sorted(targetNamedEntities, key=len)


        # learn from the other sentence that a certain word/phrase is a named entity (learn for source from target)
        for item in source:
            alreadyIncluded = False
            for jtem in sourceNamedEntities:
                if item[1] in jtem[1]:
                    alreadyIncluded = True
                    break
            if alreadyIncluded or (len(item[2]) >0 and not item[2][0].isupper()):
                continue
            for jtem in targetNamedEntities:
                if item[2] in jtem[2]:
                    # construct the item
                    newItem = [[item[0]], [item[1]], [item[2]], jtem[3]]

                    # check if the current item is part of a named entity part of which has already been added (by checking contiguousness)
                    partOfABiggerName = False
                    for k in xrange(len(sourceNamedEntities)):
                        if sourceNamedEntities[k][1][len(sourceNamedEntities[k][1])-1] == newItem[1][0] - 1:
                            sourceNamedEntities[k][0].append(newItem[0][0])
                            sourceNamedEntities[k][1].append(newItem[1][0])
                            sourceNamedEntities[k][2].append(newItem[2][0])
                            partOfABiggerName = True
                    if not partOfABiggerName:
                        sourceNamedEntities.append(newItem)
                elif isAcronym(item[2], jtem[2]) and [[item[0]], [item[1]], [item[2]], jtem[3]] not in sourceNamedEntities:
                    sourceNamedEntities.append([[item[0]], [item[1]], [item[2]], jtem[3]])



        # learn from the other sentence that a certain word/phrase is a named entity (learn for target from source)
        for item in target:
            alreadyIncluded = False
            for jtem in targetNamedEntities:
                if item[1] in jtem[1]:
                    alreadyIncluded = True
                    break
            if alreadyIncluded or (len(item[2]) >0 and not item[2][0].isupper()):
                continue
            for jtem in sourceNamedEntities:
                if item[2] in jtem[2]:
                    # construct the item
                    newItem = [[item[0]], [item[1]], [item[2]], jtem[3]]

                    # check if the current item is part of a named entity part of which has already been added (by checking contiguousness)
                    partOfABiggerName = False
                    for k in xrange(len(targetNamedEntities)):
                        if targetNamedEntities[k][1][len(targetNamedEntities[k][1])-1] == newItem[1][0] - 1:
                            targetNamedEntities[k][0].append(newItem[0][0])
                            targetNamedEntities[k][1].append(newItem[1][0])
                            targetNamedEntities[k][2].append(newItem[2][0])
                            partOfABiggerName = True
                    if not partOfABiggerName:
                        targetNamedEntities.append(newItem)
                elif isAcronym(item[2], jtem[2]) and [[item[0]], [item[1]], [item[2]], jtem[3]] not in targetNamedEntities:
                    targetNamedEntities.append([[item[0]], [item[1]], [item[2]], jtem[3]])


        sourceWords = []
        targetWords = []

        for item in sourceNamedEntities:
            for jtem in item[1]:
                if item[3] in ['PERSON', 'ORGANIZATION', 'LOCATION']:
                    sourceWords.append(source[jtem-1][2])
        for item in targetNamedEntities:
            for jtem in item[1]:
                if item[3] in ['PERSON', 'ORGANIZATION', 'LOCATION']:
                    targetWords.append(target[jtem-1][2])



        if len(sourceNamedEntities) == 0 or len(targetNamedEntities) == 0:
            return []




        sourceNamedEntitiesAlreadyAligned = []
        targetNamedEntitiesAlreadyAligned = []


        # align all full matches
        for item in sourceNamedEntities:
            if item[3] not in ['PERSON', 'ORGANIZATION', 'LOCATION']:
                continue


            # do not align if the current source entity is present more than once
            count = 0
            for ktem in sourceNamedEntities:
                if ktem[2] == item[2]:
                    count += 1
            if count > 1:
                continue


            for jtem in targetNamedEntities:
                if jtem[3] not in ['PERSON', 'ORGANIZATION', 'LOCATION']:
                    continue

                # do not align if the current target entity is present more than once
                count = 0
                for ktem in targetNamedEntities:
                    if ktem[2] == jtem[2]:
                        count += 1
                if count > 1:
                    continue


                # get rid of dots and hyphens
                canonicalItemWord = [i.replace('.', '') for i in item[2]]
                canonicalItemWord = [i.replace('-', '') for i in item[2]]
                canonicalJtemWord = [j.replace('.', '') for j in jtem[2]]
                canonicalJtemWord = [j.replace('-', '') for j in jtem[2]]

                if canonicalItemWord == canonicalJtemWord:
                    for k in xrange(len(item[1])):
                        if ([item[1][k], jtem[1][k]]) not in alignments:
                            alignments.append([item[1][k], jtem[1][k]])
                    sourceNamedEntitiesAlreadyAligned.append(item)
                    targetNamedEntitiesAlreadyAligned.append(jtem)

        # align acronyms with their elaborations
        for item in sourceNamedEntities:
            if item[3] not in ['PERSON', 'ORGANIZATION', 'LOCATION']:
                continue
            for jtem in targetNamedEntities:
                if jtem[3] not in ['PERSON', 'ORGANIZATION', 'LOCATION']:
                    continue

                if len(item[2])==1 and isAcronym(item[2][0], jtem[2]):
                    for i in xrange(len(jtem[1])):
                        if [item[1][0], jtem[1][i]] not in alignments:
                            alignments.append([item[1][0], jtem[1][i]])
                            sourceNamedEntitiesAlreadyAligned.append(item[1][0])
                            targetNamedEntitiesAlreadyAligned.append(jtem[1][i])

                elif len(jtem[2])==1 and isAcronym(jtem[2][0], item[2]):
                    for i in xrange(len(item[1])):
                        if [item[1][i], jtem[1][0]] not in alignments:
                            alignments.append([item[1][i], jtem[1][0]])
                            sourceNamedEntitiesAlreadyAligned.append(item[1][i])
                            targetNamedEntitiesAlreadyAligned.append(jtem[1][0])


        # align subset matches
        for item in sourceNamedEntities:
            if item[3] not in ['PERSON', 'ORGANIZATION', 'LOCATION'] or item in sourceNamedEntitiesAlreadyAligned:
                continue

            # do not align if the current source entity is present more than once
            count = 0
            for ktem in sourceNamedEntities:
                if ktem[2] == item[2]:
                    count += 1
            if count > 1:
                continue


            for jtem in targetNamedEntities:
                if jtem[3] not in ['PERSON', 'ORGANIZATION', 'LOCATION'] or jtem in targetNamedEntitiesAlreadyAligned:
                    continue

                if item[3] != jtem[3]:
                    continue

                # do not align if the current target entity is present more than once
                count = 0
                for ktem in targetNamedEntities:
                    if ktem[2] == jtem[2]:
                        count += 1
                if count > 1:
                    continue


                # find if the first is a part of the second
                if isSublist(item[2], jtem[2]):
                    unalignedWordIndicesInTheLongerName = []
                    for ktem in jtem[1]:
                        unalignedWordIndicesInTheLongerName.append(ktem)
                    for k in xrange(len(item[2])):
                        for l in xrange(len(jtem[2])):
                            if item[2][k] == jtem[2][l] and [item[1][k], jtem[1][l]] not in alignments:
                                alignments.append([item[1][k], jtem[1][l]])
                                if jtem[1][l] in unalignedWordIndicesInTheLongerName:
                                    unalignedWordIndicesInTheLongerName.remove(jtem[1][l])
                    for k in xrange(len(item[1])): # the shorter name
                        for l in xrange(len(jtem[1])): # the longer name
                            # find if the current term in the longer name has already been aligned (before calling alignNamedEntities()), do not align it in that case
                            alreadyInserted = False
                            for mtem in existingAlignments:
                                if mtem[1] == jtem[1][l]:
                                    alreadyInserted = True
                                    break
                            if jtem[1][l] not in unalignedWordIndicesInTheLongerName or alreadyInserted:
                                continue
                            if [item[1][k], jtem[1][l]] not in alignments  and target[jtem[1][l]-1][2] not in sourceWords  and item[2][k] not in punctuations and jtem[2][l] not in punctuations:
                                alignments.append([item[1][k], jtem[1][l]])

                # else find if the second is a part of the first
                elif isSublist(jtem[2], item[2]):
                    unalignedWordIndicesInTheLongerName = []
                    for ktem in item[1]:
                        unalignedWordIndicesInTheLongerName.append(ktem)
                    for k in xrange(len(jtem[2])):
                        for l in xrange(len(item[2])):
                            if jtem[2][k] == item[2][l] and [item[1][l], jtem[1][k]] not in alignments:
                                alignments.append([item[1][l], jtem[1][k]])
                                if item[1][l] in unalignedWordIndicesInTheLongerName:
                                    unalignedWordIndicesInTheLongerName.remove(item[1][l])
                    for k in xrange(len(jtem[1])): # the shorter name
                        for l in xrange(len(item[1])): # the longer name
                            # find if the current term in the longer name has already been aligned (before calling alignNamedEntities()), do not align it in that case
                            alreadyInserted = False
                            for mtem in existingAlignments:
                                if mtem[0] == item[1][k]:
                                    alreadyInserted = True
                                    break
                            if item[1][l] not in unalignedWordIndicesInTheLongerName or alreadyInserted:
                                continue
                            if [item[1][l], jtem[1][k]] not in alignments  and source[item[1][k]-1][2] not in targetWords  and item[2][l] not in punctuations and jtem[2][k] not in punctuations:
                                alignments.append([item[1][l], jtem[1][k]])

        return alignments


    def alignWords(self, source, target, sourceParseResult, targetParseResult):
    # source and target:: each is a list of elements of the form:
    # [[character begin offset, character end offset], word index, word, lemma, pos tag]

    # function returns the word alignments from source to target - each alignment returned is of the following form:
    # [
    #  [[source word character begin offset, source word character end offset], source word index, source word, source word lemma],
    #  [[target word character begin offset, target word character end offset], target word index, target word, target word lemma]
    # ]

        global punctuations

        sourceWordIndices = [i+1 for i in xrange(len(source))]
        targetWordIndices = [i+1 for i in xrange(len(target))]


        alignments = []
        sourceWordIndicesAlreadyAligned = []
        targetWordIndicesAlreadyAligned = []

        sourceWords = [item[2] for item in source]
        targetWords = [item[2] for item in target]

        sourceLemmas = [item[3] for item in source]
        targetLemmas = [item[3] for item in target]

        sourcePosTags = [item[4] for item in source]
        targetPosTags = [item[4] for item in target]


        # align the sentence ending punctuation first
        if (sourceWords[len(source)-1] in ['.', '!'] and targetWords[len(target)-1] in ['.', '!']) or sourceWords[len(source)-1] == targetWords[len(target)-1]:
            alignments.append([len(source), len(target)])
            sourceWordIndicesAlreadyAligned.append(len(source))
            targetWordIndicesAlreadyAligned.append(len(target))
        elif sourceWords[len(source)-2] in ['.', '!'] and targetWords[len(target)-1] in ['.', '!']:
            alignments.append([len(source)-1, len(target)])
            sourceWordIndicesAlreadyAligned.append(len(source)-1)
            targetWordIndicesAlreadyAligned.append(len(target))
        elif sourceWords[len(source)-1] in ['.', '!'] and targetWords[len(target)-2] in ['.', '!']:
            alignments.append([len(source), len(target)-1])
            sourceWordIndicesAlreadyAligned.append(len(source))
            targetWordIndicesAlreadyAligned.append(len(target)-1)
        elif sourceWords[len(source)-2] in ['.', '!'] and targetWords[len(target)-2] in ['.', '!']:
            alignments.append([len(source)-1, len(target)-1])
            sourceWordIndicesAlreadyAligned.append(len(source)-1)
            targetWordIndicesAlreadyAligned.append(len(target)-1)

        # align all (>=2)-gram matches with at least one content word
        commonContiguousSublists = findAllCommonContiguousSublists(sourceWords, targetWords, True)

        for item in commonContiguousSublists:
            allStopWords = True
            for sourceWord in item[0]:
                if sourceWords[sourceWord] not in stopwords and sourceWords[sourceWord] not in punctuations:
                    allStopWords = False
                    break
            for targetWord in item[1]:
                if targetWords[targetWord] not in stopwords and targetWords[targetWord] not in punctuations:
                    allStopWords = False
                    break
            if len(item[0]) >= 2 and not allStopWords:
                for j in xrange(len(item[0])):
                    if item[0][j]+1 not in sourceWordIndicesAlreadyAligned and item[1][j]+1 not in targetWordIndicesAlreadyAligned and [item[0][j]+1, item[1][j]+1] not in alignments:
                        alignments.append([item[0][j]+1, item[1][j]+1])
                        sourceWordIndicesAlreadyAligned.append(item[0][j]+1)
                        targetWordIndicesAlreadyAligned.append(item[1][j]+1)

        # align hyphenated word groups
        for i in sourceWordIndices:
            if i in sourceWordIndicesAlreadyAligned:
                continue
            if '-' in sourceWords[i-1] and sourceWords[i-1] != '-':
                tokens = sourceWords[i-1].split('-')
                commonContiguousSublists = findAllCommonContiguousSublists(tokens, targetWords)
                for item in commonContiguousSublists:
                    if len(item[0]) > 1:
                        for jtem in item[1]:
                            if [i, jtem+1] not in alignments:
                                alignments.append([i, jtem+1])
                                sourceWordIndicesAlreadyAligned.append(i)
                                targetWordIndicesAlreadyAligned.append(jtem+1)

        for i in targetWordIndices:
            if i in targetWordIndicesAlreadyAligned:
                continue
            if '-' in target[i-1][2] and target[i-1][2] != '-':
                tokens = target[i-1][2].split('-')
                commonContiguousSublists = findAllCommonContiguousSublists(sourceWords, tokens)
                for item in commonContiguousSublists:
                    if len(item[0]) > 1:
                        for jtem in item[0]:
                            if [jtem+1, i] not in alignments:
                                alignments.append([jtem+1, i])
                                sourceWordIndicesAlreadyAligned.append(jtem+1)
                                targetWordIndicesAlreadyAligned.append(i)

        # align named entities
        neAlignments = self.alignNamedEntities(source, target, sourceParseResult, targetParseResult, alignments)
        for item in neAlignments:
            if item not in alignments:
                alignments.append(item)
                if item[0] not in sourceWordIndicesAlreadyAligned:
                    sourceWordIndicesAlreadyAligned.append(item[0])
                if item[1] not in targetWordIndicesAlreadyAligned:
                    targetWordIndicesAlreadyAligned.append(item[1])

        # align words based on word and dependency match
        sourceDParse = dependencyParseAndPutOffsets(sourceParseResult)
        targetDParse = dependencyParseAndPutOffsets(targetParseResult)

        mainVerbAlignments = self.alignPos('verb', 'v', source, target, sourceParseResult, targetParseResult, alignments)
        for item in mainVerbAlignments:
            if item not in alignments:
                alignments.append(item)
                if item[0] not in sourceWordIndicesAlreadyAligned:
                    sourceWordIndicesAlreadyAligned.append(item[0])
                if item[1] not in targetWordIndicesAlreadyAligned:
                    targetWordIndicesAlreadyAligned.append(item[1])

        nounAlignments = self.alignPos('noun', 'n', source, target, sourceParseResult, targetParseResult, alignments)
        for item in nounAlignments:
            if item not in alignments:
                alignments.append(item)
                if item[0] not in sourceWordIndicesAlreadyAligned:
                    sourceWordIndicesAlreadyAligned.append(item[0])
                if item[1] not in targetWordIndicesAlreadyAligned:
                    targetWordIndicesAlreadyAligned.append(item[1])

        adjectiveAlignments = self.alignPos('adjective', 'j', source,  target, sourceParseResult, targetParseResult, alignments)
        for item in adjectiveAlignments:
            if item not in alignments:
                alignments.append(item)
                if item[0] not in sourceWordIndicesAlreadyAligned:
                    sourceWordIndicesAlreadyAligned.append(item[0])
                if item[1] not in targetWordIndicesAlreadyAligned:
                    targetWordIndicesAlreadyAligned.append(item[1])

        adverbAlignments = self.alignPos('adverb', 'r', source, target, sourceParseResult, targetParseResult, alignments)
        for item in adverbAlignments:
            if item not in alignments:
                alignments.append(item)
                if item[0] not in sourceWordIndicesAlreadyAligned:
                    sourceWordIndicesAlreadyAligned.append(item[0])
                if item[1] not in targetWordIndicesAlreadyAligned:
                    targetWordIndicesAlreadyAligned.append(item[1])

        # collect evidence from textual neighborhood for aligning content words
        wordSimilarities = {}
        textualNeighborhoodSimilarities = {}
        sourceWordIndicesBeingConsidered = []
        targetWordIndicesBeingConsidered = []

        for i in sourceWordIndices:
            if i in sourceWordIndicesAlreadyAligned or sourceLemmas[i-1] in stopwords + punctuations + ['\'s', '\'d', '\'ll']:
                continue

            for j in targetWordIndices:
                if j in targetWordIndicesAlreadyAligned or targetLemmas[j-1] in stopwords + punctuations + ['\'s', '\'d', '\'ll']:
                    continue

                wordSimilarities[(i, j)] = max(wordRelatedness(sourceWords[i-1], sourcePosTags[i-1], targetWords[j-1], targetPosTags[j-1], self.scorer), wordRelatedness(sourceLemmas[i-1], sourcePosTags[i-1], targetLemmas[j-1], targetPosTags[j-1], self.scorer))
                sourceWordIndicesBeingConsidered.append(i)
                targetWordIndicesBeingConsidered.append(j)


                # textual neighborhood similarities
                sourceNeighborhood = findTextualNeighborhood(source, i, 3, 3)
                targetNeighborhood = findTextualNeighborhood(target, j, 3, 3)
                evidence = 0
                for k in xrange(len(sourceNeighborhood[0])):
                    for l in xrange(len(targetNeighborhood[0])):
                          if (sourceNeighborhood[1][k] not in stopwords + punctuations) and ((sourceNeighborhood[0][k], targetNeighborhood[0][l]) in alignments or (wordRelatedness(sourceNeighborhood[1][k], 'none', targetNeighborhood[1][l], 'none', self.scorer) >= self.config.similarity_threshold)):
                            evidence += wordRelatedness(sourceNeighborhood[1][k], 'none', targetNeighborhood[1][l], 'none', self.scorer)
                textualNeighborhoodSimilarities[(i, j)] = evidence

        numOfUnalignedWordsInSource = len(set(sourceWordIndicesBeingConsidered))

        # now align: find the best alignment in each iteration of the following loop and include in alignments if good enough
        for item in xrange(numOfUnalignedWordsInSource):
            highestWeightedSim = 0
            bestWordSim = 0
            bestSourceIndex = -1
            bestTargetIndex = -1

            for i in set(sourceWordIndicesBeingConsidered):
                if i in sourceWordIndicesAlreadyAligned:
                    continue

                for j in set(targetWordIndicesBeingConsidered):
                    if j in targetWordIndicesAlreadyAligned:
                        continue

                    if (i, j) not in wordSimilarities:
                        continue

                    theta2 = 1 - theta1
                    if theta1*wordSimilarities[(i, j)] + theta2*textualNeighborhoodSimilarities[(i, j)] > highestWeightedSim:
                        highestWeightedSim = theta1*wordSimilarities[(i, j)] + theta2*textualNeighborhoodSimilarities[(i, j)]
                        bestSourceIndex = i
                        bestTargetIndex = j
                        bestWordSim = wordSimilarities[(i, j)]
                        bestTextNeighborhoodSim = textualNeighborhoodSimilarities[(i, j)]

            if bestWordSim >= self.config.similarity_threshold and [bestSourceIndex, bestTargetIndex] not in alignments and bestSourceIndex not in sourceWordIndicesAlreadyAligned and bestTargetIndex not in targetWordIndicesAlreadyAligned:
                if sourceLemmas[bestSourceIndex-1] not in stopwords:
                    alignments.append([bestSourceIndex, bestTargetIndex])
                    sourceWordIndicesAlreadyAligned.append(bestSourceIndex)
                    targetWordIndicesAlreadyAligned.append(bestTargetIndex)

            if bestSourceIndex in sourceWordIndicesBeingConsidered:
                sourceWordIndicesBeingConsidered.remove(bestSourceIndex)
            if bestTargetIndex in targetWordIndicesBeingConsidered:
                targetWordIndicesBeingConsidered.remove(bestTargetIndex)

         # look if any remaining word is a part of a hyphenated word
        for i in sourceWordIndices:
            if i in sourceWordIndicesAlreadyAligned:
                continue
            if '-' in sourceWords[i-1] and sourceWords[i-1] != '-':
                tokens = sourceWords[i-1].split('-')
                commonContiguousSublists = findAllCommonContiguousSublists(tokens, targetWords)
                for item in commonContiguousSublists:
                    if len(item[0]) == 1 and target[item[1][0]][3] not in stopwords:
                        for jtem in item[1]:
                            if [i, jtem+1] not in alignments and jtem+1 not in targetWordIndicesAlreadyAligned:
                                alignments.append([i, jtem+1])
                                sourceWordIndicesAlreadyAligned.append(i)
                                targetWordIndicesAlreadyAligned.append(jtem+1)

        for i in targetWordIndices:
            if i in targetWordIndicesAlreadyAligned:
                continue
            if '-' in target[i-1][2] and target[i-1][2] != '-':
                tokens = target[i-1][2].split('-')
                commonContiguousSublists = findAllCommonContiguousSublists(sourceWords, tokens)
                for item in commonContiguousSublists:
                    if len(item[0]) == 1 and source[item[0][0]][3] not in stopwords:
                        for jtem in item[0]:
                            if [jtem+1, i] not in alignments and i not in targetWordIndicesAlreadyAligned:
                                alignments.append([jtem+1, i])
                                sourceWordIndicesAlreadyAligned.append(jtem+1)
                                targetWordIndicesAlreadyAligned.append(i)

        # collect evidence from dependency neighborhood for aligning stopwords
        wordSimilarities = {}
        dependencyNeighborhoodSimilarities = {}
        sourceWordIndicesBeingConsidered = []
        targetWordIndicesBeingConsidered = []

        for i in sourceWordIndices:
            if sourceLemmas[i-1] not in stopwords or i in sourceWordIndicesAlreadyAligned:
                continue

            for j in targetWordIndices:
                if targetLemmas[j-1] not in stopwords or j in targetWordIndicesAlreadyAligned:
                    continue

                if (sourceLemmas[i-1] != targetLemmas[j-1]) and (wordRelatedness(sourceLemmas[i-1], sourcePosTags[i-1], targetLemmas[j-1], targetPosTags[j-1], self.scorer) < self.config.similarity_threshold):
                    continue

                wordSimilarities[(i, j)] = max(wordRelatedness(sourceWords[i-1], sourcePosTags[i-1], targetWords[j-1], targetPosTags[j-1], self.scorer), wordRelatedness(sourceLemmas[i-1], sourcePosTags[i-1], targetLemmas[j-1], targetPosTags[j-1], self.scorer))

                sourceWordIndicesBeingConsidered.append(i)
                targetWordIndicesBeingConsidered.append(j)

                sourceWordParents = findParents(sourceDParse, i, sourceWords[i-1])
                sourceWordChildren = findChildren(sourceDParse, i, sourceWords[i-1])
                targetWordParents = findParents(targetDParse, j, targetWords[j-1])
                targetWordChildren = findChildren(targetDParse, j, targetWords[j-1])

                evidence = 0

                for item in sourceWordParents:
                    for jtem in targetWordParents:
                        if [item[0], jtem[0]] in alignments:
                            evidence += 1
                for item in sourceWordChildren:
                    for jtem in targetWordChildren:
                        if [item[0], jtem[0]] in alignments:
                            evidence += 1

                dependencyNeighborhoodSimilarities[(i, j)] = evidence

        numOfUnalignedWordsInSource = len(set(sourceWordIndicesBeingConsidered))

        # now align: find the best alignment in each iteration of the following loop and include in alignments if good enough
        for item in xrange(numOfUnalignedWordsInSource):
            highestWeightedSim = 0
            bestWordSim = 0
            bestSourceIndex = -1
            bestTargetIndex = -1

            for i in set(sourceWordIndicesBeingConsidered):
                for j in set(targetWordIndicesBeingConsidered):
                    if (i, j) not in wordSimilarities:
                        continue
                    theta2 = 1 - theta1
                    if theta1*wordSimilarities[(i, j)] + theta2*dependencyNeighborhoodSimilarities[(i, j)] > highestWeightedSim:
                        highestWeightedSim = theta1*wordSimilarities[(i, j)] + theta2*dependencyNeighborhoodSimilarities[(i, j)]
                        bestSourceIndex = i
                        bestTargetIndex = j
                        bestWordSim = wordSimilarities[(i, j)]
                        bestDependencyNeighborhoodSim = dependencyNeighborhoodSimilarities[(i, j)]

            if bestWordSim >= self.config.similarity_threshold and bestDependencyNeighborhoodSim > 0 and [bestSourceIndex, bestTargetIndex] not in alignments and bestSourceIndex not in sourceWordIndicesAlreadyAligned and bestTargetIndex not in targetWordIndicesAlreadyAligned:
                alignments.append([bestSourceIndex, bestTargetIndex])
                sourceWordIndicesAlreadyAligned.append(bestSourceIndex)
                targetWordIndicesAlreadyAligned.append(bestTargetIndex)

            if bestSourceIndex in sourceWordIndicesBeingConsidered:
                sourceWordIndicesBeingConsidered.remove(bestSourceIndex)
            if bestTargetIndex in targetWordIndicesBeingConsidered:
                targetWordIndicesBeingConsidered.remove(bestTargetIndex)

        # collect evidence from textual neighborhood for aligning stopwords and punctuations
        wordSimilarities = {}
        textualNeighborhoodSimilarities = {}
        sourceWordIndicesBeingConsidered = []
        targetWordIndicesBeingConsidered = []

        for i in sourceWordIndices:
            if (sourceLemmas[i-1] not in stopwords + punctuations + ['\'s', '\'d', '\'ll']) or i in sourceWordIndicesAlreadyAligned:
                continue

            for j in targetWordIndices:
                if (targetLemmas[j-1] not in stopwords + punctuations + ['\'s', '\'d', '\'ll']) or j in targetWordIndicesAlreadyAligned:
                    continue

                if wordRelatedness(sourceLemmas[i-1], sourcePosTags[i-1], targetLemmas[j-1], targetPosTags[j-1], self.scorer) < self.config.similarity_threshold:
                    continue


                wordSimilarities[(i, j)] = max(wordRelatedness(sourceWords[i-1], sourcePosTags[i-1], targetWords[j-1], targetPosTags[j-1], self.scorer), wordRelatedness(sourceLemmas[i-1], sourcePosTags[i-1], targetLemmas[j-1], targetPosTags[j-1], self.scorer))

                sourceWordIndicesBeingConsidered.append(i)
                targetWordIndicesBeingConsidered.append(j)

                # textual neighborhood evidence, increasing evidence if content words around this stop word are aligned
                evidence = 0

                k = i
                l = j

                while k > 0:
                    if sourceLemmas[k-1] in stopwords + punctuations + ['\'s', '\'d', '\'ll']:
                        k -= 1
                    else:
                        break
                while l > 0:
                    if targetLemmas[l-1] in stopwords + punctuations + ['\'s', '\'d', '\'ll']:
                        l -= 1
                    else:
                        break

                m = i
                n = j


                while m < len(sourceLemmas) - 1:
                    if sourceLemmas[m - 1] in stopwords + punctuations + ['\'s', '\'d', '\'ll']:

                        m += 1
                    else:
                        break
                while n < len(targetLemmas) - 1:
                    if targetLemmas[n - 1] in stopwords + punctuations + ['\'s', '\'d', '\'ll']:
                        n += 1
                    else:
                        break

                if [k, l] in alignments:
                    evidence += 1

                if [m, n] in alignments:
                    evidence += 1

                textualNeighborhoodSimilarities[(i, j)] = evidence

        numOfUnalignedWordsInSource = len(set(sourceWordIndicesBeingConsidered))

        # now align: find the best alignment in each iteration of the following loop and include in alignments if good enough
        for item in xrange(numOfUnalignedWordsInSource):
            highestWeightedSim = 0
            bestWordSim = 0
            bestSourceIndex = -1
            bestTargetIndex = -1

            for i in set(sourceWordIndicesBeingConsidered):
                if i in sourceWordIndicesAlreadyAligned:
                    continue

                for j in set(targetWordIndicesBeingConsidered):
                    if j in targetWordIndicesAlreadyAligned:
                        continue

                    if (i, j) not in wordSimilarities:
                        continue


                    theta2 = 1 - theta1
                    if theta1*wordSimilarities[(i, j)] + theta2*textualNeighborhoodSimilarities[(i, j)] > highestWeightedSim:
                        highestWeightedSim = theta1*wordSimilarities[(i, j)] + theta2*textualNeighborhoodSimilarities[(i, j)]
                        bestSourceIndex = i
                        bestTargetIndex = j
                        bestWordSim = wordSimilarities[(i, j)]
                        bestTextNeighborhoodSim = textualNeighborhoodSimilarities[(i, j)]

            if bestWordSim >= self.config.similarity_threshold and bestTextNeighborhoodSim > 0 and [bestSourceIndex, bestTargetIndex] not in alignments and bestSourceIndex not in sourceWordIndicesAlreadyAligned and bestTargetIndex not in targetWordIndicesAlreadyAligned:
                alignments.append([bestSourceIndex, bestTargetIndex])
                sourceWordIndicesAlreadyAligned.append(bestSourceIndex)
                targetWordIndicesAlreadyAligned.append(bestTargetIndex)

            if bestSourceIndex in sourceWordIndicesBeingConsidered:
                sourceWordIndicesBeingConsidered.remove(bestSourceIndex)
            if bestTargetIndex in targetWordIndicesBeingConsidered:
                targetWordIndicesBeingConsidered.remove(bestTargetIndex)

        alignments = [item for item in alignments if item[0] != 0 and item[1] != 0]

        return alignments

    def updateDuplicationSimilarity(self, aligments, aligmentSimilarity):
        for i, a in enumerate(aligments):
            for j, b in enumerate(aligments):
                if (a[0] == b[0] and a != b) or (a[1] == b[1] and a != b):
                    if aligmentSimilarity[j] > aligmentSimilarity[i]:
                        aligmentSimilarity[i] = aligmentSimilarity[j]
                    else:
                        aligmentSimilarity[j] = aligmentSimilarity[i]

        return aligments, aligmentSimilarity

    def align(self, sentence1, sentence2):
        sentence1ParseResult = parseText(sentence1)
        sentence2ParseResult = parseText(sentence2)

        sentence1LemmasAndPosTags = prepareSentence(sentence1)
        sentence2LemmasAndPosTags = prepareSentence(sentence2)

        myWordAlignments = self.alignWords(sentence1LemmasAndPosTags, sentence2LemmasAndPosTags, sentence1ParseResult, sentence2ParseResult)
        myWordDependencySimilarity = []

        for pair in myWordAlignments:
            sourceWord = sentence1LemmasAndPosTags[pair[0] - 1]
            targetWord = sentence2LemmasAndPosTags[pair[1] - 1]
            myWordDependencySimilarity.append(self.calculateDependencySimilarity(sourceWord,  pair[0], targetWord, pair[1], sentence1LemmasAndPosTags, sentence2LemmasAndPosTags, sentence1ParseResult, sentence2ParseResult, myWordAlignments))

        myWordAlignments, myWordDependencySimilarity = self.updateDuplicationSimilarity(myWordAlignments, myWordDependencySimilarity)

        myWordAlignmentTokens = [[sentence1LemmasAndPosTags[item[0]-1][2], sentence2LemmasAndPosTags[item[1]-1][2]] for item in myWordAlignments]
        return [myWordAlignments, myWordAlignmentTokens, myWordDependencySimilarity]

    def calculateDependencySimilarity(self, sourceWord, sourceIndex, targetWord, targetIndex, sourceSentence, targetSentence, sourceParseResult, targetParseResult, alignments):
        sourceLemmas = [item[3] for item in sourceSentence]
        targetLemmas = [item[3] for item in targetSentence]

        sourcePosTags = [item[4] for item in sourceSentence]
        targetPosTags = [item[4] for item in targetSentence]

        sourceDParse = dependencyParseAndPutOffsets(sourceParseResult)
        targetDParse = dependencyParseAndPutOffsets(targetParseResult)


        evidence = 0
        normalizedEvidence = 0

        pos = ''
        if sourceWord[4].lower().startswith('v'):
            pos = 'verb'
        if sourceWord[4].lower().startswith('n'):
            pos = 'noun'
        if sourceWord[4].lower().startswith('j'):
            pos = 'adjective'
        if sourceWord[4].lower().startswith('r'):
            pos = 'adverb'

        sourceWordParents = findParents(sourceDParse, sourceIndex, sourceWord[2])
        sourceWordChildren = findChildren(sourceDParse, sourceIndex, sourceWord[2])
        targetWordParents = findParents(targetDParse, targetIndex, targetWord[2])
        targetWordChildren = findChildren(targetDParse, targetIndex, targetWord[2])


        if len(pos) > 0:
            context = self.findDependencySimilarity(pos, sourceWord[2], sourceIndex, targetWord[2], targetIndex, sourceDParse, targetDParse, alignments, sourcePosTags, targetPosTags, sourceLemmas, targetLemmas)
            evidence = context[0]
        else:
            for item in sourceWordParents:
                for jtem in targetWordParents:
                    if [item[0], jtem[0]] in alignments:
                        evidence += 1

            for item in sourceWordChildren:
                for jtem in targetWordChildren:
                    if [item[0], jtem[0]] in alignments:
                            evidence += 1

        totalContext = len(targetWordChildren) + len(targetWordParents) + 1.0
        normalizedEvidence += (evidence/totalContext - 1) * math.log(totalContext)

        return normalizedEvidence




