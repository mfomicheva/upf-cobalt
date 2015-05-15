from config import *
from nltk.corpus import wordnet
import re
import math
from types import *

def wordRelatednessAlignment(word1, word2, config):

    global stemmer
    global punctuations

    canonical_word1 = canonize_word(word1.form)
    canonical_word2 = canonize_word(word2.form)

    if canonical_word1.isdigit() and canonical_word2.isdigit() and canonical_word1 != canonical_word2:
        return 0

    if word1.pos.lower() == 'cd' and word2.pos.lower() == 'cd' and (not canonical_word1.isdigit() and not canonical_word2.isdigit()) and canonical_word1 <> canonical_word2:
        return 0

    # stopwords can be similar to only stopwords
    if (canonical_word1 in stopwords and canonical_word2 not in stopwords) or (canonical_word1 not in stopwords and canonical_word2 in stopwords):
        return 0

    # punctuations can only be either identical or totally dissimilar
    if canonical_word1 in punctuations or canonical_word2 in punctuations:
        return 0

    if canonical_word1 == canonical_word2:
        lexSim = config.exact

    elif contractionDictionary.check_contraction(canonical_word1, canonical_word2):
        lexSim = config.exact

    elif stemmer.stem(canonical_word1) == stemmer.stem(canonical_word2):
        lexSim = config.stem

    elif word1.lemma == word2.lemma:
        lexSim = config.stem

    elif synonymDictionary.checkSynonymByLemma(word1.lemma, word2.lemma):
        lexSim = config.synonym

    elif presentInPPDB(canonical_word1, canonical_word2):
        lexSim = config.paraphrase

    elif ((not functionWord(word1.form) and not functionWord(word2.form)) or word1.pos[0] == word2.pos[0]) and cosineSimilarity(word1.form, word2.form) > config.related_threshold:

        if word1.form not in punctuations and word2.form not in punctuations:
            lexSim = config.related

    else:
        lexSim = 0.0

    return lexSim

def wordRelatednessScoring(word1, word2, scorer, contextPenalty):

    global stemmer
    global punctuations

    canonical_word1 = canonize_word(word1.form)
    canonical_word2 = canonize_word(word2.form)

    if canonical_word1 == canonical_word2:
        lexSim = scorer.exact

    elif contractionDictionary.check_contraction(canonical_word1, canonical_word2):
        lexSim = scorer.exact

    elif word1.lemma == word2.lemma:
        lexSim = scorer.stem

    elif stemmer.stem(canonical_word1) == stemmer.stem(canonical_word2):
        lexSim = scorer.stem

    elif synonymDictionary.checkSynonymByLemma(word1.lemma, word2.lemma):
        lexSim = scorer.synonym

    elif presentInPPDB(canonical_word1, canonical_word2):
        lexSim = scorer.paraphrase

    elif ((not functionWord(word1.form) and not functionWord(word2.form)) or word1.pos[0] == word2.pos[0]) and cosineSimilarity(word1.form, word2.form) > scorer.related_threshold:
        lexSim = scorer.related

    else:
        lexSim = 0.0

    result = lexSim - contextPenalty * scorer.context_importance

    return max(result, scorer.minimal_aligned_relatedness)

def wordnetPathSimilarity(word1, word2):

    synsets1 = wordnet.synsets(word1)
    synsets2 = wordnet.synsets(word2)

    max_similarity = 0

    for synset1 in synsets1:
        for synset2 in synsets2:
            if synset1._pos == synset2._pos:
                similarity = wordnet.path_similarity(synset1, synset2)
            else:
                similarity = 0
            if max_similarity < similarity:
                max_similarity = similarity

    return max_similarity

def loadWordVectors(vectorsFileName = '/home/tos/workspace/distributed-similarity/deps.words'):

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

def cosineSimilarity(word1, word2):

    global wordVector

    if word1.lower() in wordVector and word2.lower() in wordVector:
        vector1 = wordVector[word1.lower()].split( )
        vector2 = wordVector[word2.lower()].split( )
        sumxx, sumxy, sumyy = 0, 0, 0

        for i in range(len(vector1)):
            x = float(vector1[i])
            y = float(vector2[i])
            sumxx += x * x
            sumyy += y * y
            sumxy += x * y
        return sumxy/math.sqrt(sumxx * sumyy)
    else:
        return 0

def loadPosWordVectors(vectorsFileName = '/home/u88591/Workspace/distributional-similarity/vectors_ukwac_tagged.txt'):

    global posVector
    vectorFile = open(vectorsFileName, 'r')

    for line in vectorFile:
        if line == '\n':
            continue

        match = re.match(r'^([^ ]+) (.+)',line)
        if type(match) is NoneType:
            continue

        wordExpression = match.group(1).split('/')

        if len(wordExpression) != 2 or len(wordExpression[1]) == 0:
            continue

        pos = wordExpression[1][0].lower()
        word = wordExpression[0]

        if not pos in posVector:
            posVector[pos] = {}

        wordVector = posVector[pos]
        wordVector[word] = match.group(2)

def posCosineSimilarity(word1, word2):

    global posVector
    global punctuations

    pos1 = word1.pos[0].lower()
    pos2 = word2.pos[0].lower()
    if pos1 in punctuations or pos2 in punctuations:
        return 0

    wordVector1 = posVector[pos1]
    wordVector2 = posVector[pos2]

    if word1.lemma.lower() in wordVector1 and word2.lemma.lower() in wordVector2:
        vector1 = wordVector1[word1.lemma.lower()]
        vector2 = wordVector2[word2.lemma.lower()]

        if not type(vector1) is list:
            vector = []
            for v in vector1.split():
                vector.append(float(v))
            wordVector1[word1.lemma.lower()] = vector
            vector1 = vector

        if not type(vector2) is list:
            vector = []
            for v in vector2.split():
                vector.append(float(v))
            wordVector2[word2.lemma.lower()] = vector
            vector2 = vector

        sumxx, sumxy, sumyy = 0, 0, 0

        for i in range(len(vector1)):
            x = vector1[i]
            y = vector2[i]
            sumxx += x * x
            sumyy += y * y
            sumxy += x * y
        return sumxy/math.sqrt(sumxx * sumyy)
    else:
        return 0

def loadPPDB(ppdbFileName = 'Resources/ppdb-1.0-xxxl-lexical.extended.synonyms.uniquepairs'):

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


def presentInPPDB(word1, word2):
    global ppdbDict

    if (word1.lower(), word2.lower()) in ppdbDict:
        return True
    if (word2.lower(), word1.lower()) in ppdbDict:
        return True


def functionWord(word):
    global punctuations
    return (word.lower() in stopwords) or (word.lower() in punctuations)


def canonize_word(word):
    if len(word) > 1:
        canonical_form = word.replace('.', '')
        canonical_form = canonical_form.replace('-', '')
        canonical_form = canonical_form.replace(',', '').lower()
    else:
        canonical_form = word.lower()

    return canonical_form


def comparePos (pos1, pos2, scorer):

    if pos1 == pos2:
        posSim = scorer.posExact
    elif pos1[0] == pos2[0]:
        posSim = scorer.posGramCat
    else:
        posSim = scorer.posNone

    return posSim


loadPPDB()
loadWordVectors()
