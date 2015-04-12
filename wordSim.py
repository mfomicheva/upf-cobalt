from config import *
from nltk.corpus import wordnet
import re
import math
from types import *

def loadWordVectors(vectorsFileName = 'Resources/vectors/deps.words'):

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

def cosineSimilarity(word1,word2):

    global wordVector

    if word1.lower() in wordVector and word2.lower() in wordVector:
        vector1 = wordVector[word1.lower()].split( )
        vector2 = wordVector[word2.lower()].split( )
        sumxx, sumxy, sumyy = 0, 0, 0

        for i in range(len(vector1)):
            x = float(vector1[i])
            y = float(vector2[i])
            sumxx += x*x
            sumyy += y*y
            sumxy += x*y
        return sumxy/math.sqrt(sumxx*sumyy)
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


def wordnetSimilarity(word1, word2):

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


def wordRelatedness(word1, lemma1, pos1, word2, lemma2, pos2, config):
    global stemmer
    global punctuations

    canonical_word1 = canonize_word(word1)
    canonical_word2 = canonize_word(word2)

    if canonical_word1 == canonical_word2:
        return config.exact

    if stemmer.stem(canonical_word1) == stemmer.stem(canonical_word2):
        return config.stem

    if lemma1 == lemma2:
        return config.stem

    if canonical_word1.isdigit() and canonical_word2.isdigit() and canonical_word1 != canonical_word2:
        return 0

    if pos1.lower() == 'cd' and pos2.lower() == 'cd' and (not canonical_word1.isdigit() and not canonical_word2.isdigit()) and canonical_word1 <> canonical_word2:
        return 0

    # stopwords can be similar to only stopwords
    if (canonical_word1 in stopwords and canonical_word2 not in stopwords) or (canonical_word1 not in stopwords and canonical_word2 in stopwords):
        return 0

    # punctuations can only be either identical or totally dissimilar
    if canonical_word1 in punctuations or canonical_word2 in punctuations:
        return 0

    if synonymDictionary.checkSynonymByLemma(canonical_word1, canonical_word2):
        return config.synonym

    elif synonymDictionary.checkSynonymByLemma(lemma1, lemma2):
        return config.synonym

    elif presentInPPDB(canonical_word1, canonical_word2):
        return config.paraphrase

    elif presentInPPDB(lemma1, lemma2):
        return config.paraphrase

    # elif not functionWord(canonical_word1) and not functionWord(canonical_word1) and wordnetSimilarity(lemma1, lemma2) > config.related_threshold:
    #     return config.related

    elif cosineSimilarity(lemma1, lemma2) > config.related_threshold:
        return config.related

    else:
        return 0


def weightedWordRelatedness(word1, word2, scorer, contextPenalty):
    global stemmer
    global punctuations

    lexSim = 0
    posSim = 0
    wordSim = 0
    result = 0

    canonical_word1 = canonize_word(word1.form)
    canonical_word2 = canonize_word(word2.form)

    if canonical_word1 == canonical_word2:
        lexSim = scorer.exact

    elif contractionDictionary.check_contraction(canonical_word1, canonical_word2):
        lexSim = scorer.exact

    elif word1.lemma == word2.lemma:
        lexSim = scorer.exact

    elif stemmer.stem(canonical_word1) == stemmer.stem(canonical_word2):
        lexSim = scorer.exact

    elif synonymDictionary.checkSynonymByLemma(canonical_word1, canonical_word2):
        lexSim = scorer.synonym

    elif synonymDictionary.checkSynonymByLemma(word1.lemma, word2.lemma):
        lexSim = scorer.synonym

    elif presentInPPDB(word1.form, word2.form):
        lexSim = scorer.paraphrase

    elif presentInPPDB(canonical_word1, canonical_word2):
        lexSim = scorer.paraphrase

    elif presentInPPDB(word1.lemma, word2.lemma):
        lexSim = scorer.paraphrase

    # elif not functionWord(canonical_word1) and not functionWord(canonical_word1) and wordnetSimilarity(word1.lemma, word2.lemma) > scorer.related_threshold:
    #     lexSim = scorer.related

    elif cosineSimilarity(word1.lemma, word2.lemma) > scorer.related_threshold:
       lexSim = scorer.related


    posSim = comparePos(word1.pos,word2.pos)
    wordSim = lexSim + (posSim - 1)
    result = wordSim + contextPenalty*scorer.context_importance
    resultThreshold = max(result, scorer.minimal_aligned_relatedness)

    return result

def comparePos (pos1,pos2):

    if pos1 == pos2:
        posSim = 1
    elif pos1[0] == pos2[0]:
        posSim = 0.8
    else:
        posSim = 0.6

    return posSim


loadPPDB()
loadWordVectors()
