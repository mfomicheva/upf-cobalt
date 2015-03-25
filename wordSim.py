from config import *
from nltk.corpus import wordnet


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
    return (word.form.lower() in stopwords) or (word.form.lower() in punctuations)


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


def wordRelatedness(word1, pos1, word2, pos2, config):
    global stemmer
    global punctuations

    if len(word1) > 1:
        canonicalWord1 = word1.replace('.', '')
        canonicalWord1 = canonicalWord1.replace('-', '')
        canonicalWord1 = canonicalWord1.replace(',', '')
    else:
        canonicalWord1 = word1
        
    if len(word2) > 1:
        canonicalWord2 = word2.replace('.', '')
        canonicalWord2 = canonicalWord2.replace('-', '')
        canonicalWord2 = canonicalWord2.replace(',', '')
    else:
        canonicalWord2 = word2
    
    if canonicalWord1.lower() == canonicalWord2.lower():
        return config.exact

    if stemmer.stem(word1).lower() == stemmer.stem(word2).lower():
        return config.exact

    if canonicalWord1.isdigit() and canonicalWord2.isdigit() and canonicalWord1 <> canonicalWord2:
        return 0

    if pos1.lower() == 'cd' and pos2.lower() == 'cd' and (not canonicalWord1.isdigit() and not canonicalWord2.isdigit()) and canonicalWord1 <> canonicalWord2:
        return 0

    # stopwords can be similar to only stopwords
    if (word1.lower() in stopwords and word2.lower() not in stopwords) or (word1.lower() not in stopwords and word2.lower() in stopwords):
        return 0

    # punctuations can only be either identical or totally dissimilar
    if word1 in punctuations or word2 in punctuations:
        return 0

    if synonymDictionary.checkSynonymByLemma(word1, word2):
        return config.synonym

    elif presentInPPDB(word1, word2):
        return config.paraphrase

    elif wordnetSimilarity(word1, word2) > config.related_threshold:
        return config.related

    else:
        return 0


def maxWeightedWordRelatedness(word1, word2, scorer, contextPenalty):
    relatedness = max(weightedWordRelatedness(word1.form, word2.form, scorer, contextPenalty, scorer.exact),
                      weightedWordRelatedness(word1.lemma, word2.lemma, scorer, contextPenalty, scorer.stem))

    return max(relatedness, scorer.minimal_aligned_relatedness)


def weightedWordRelatedness(form1, form2, scorer, contextPenalty, matchScore):
    global stemmer
    global punctuations

    result = 0

    if len(form1) > 1:
        canonicalWord1 = form1.replace('.', '')
        canonicalWord1 = canonicalWord1.replace('-', '')
        canonicalWord1 = canonicalWord1.replace(',', '')
    else:
        canonicalWord1 = form1

    if len(form2) > 1:
        canonicalWord2 = form2.replace('.', '')
        canonicalWord2 = canonicalWord2.replace('-', '')
        canonicalWord2 = canonicalWord2.replace(',', '')
    else:
        canonicalWord2 = form2

    if canonicalWord1.lower() == canonicalWord2.lower():
        result = matchScore

    elif stemmer.stem(form1).lower() == stemmer.stem(form2).lower():
        result = scorer.stem

    elif synonymDictionary.checkSynonymByLemma(form1, form2):
        result = scorer.synonym

    elif presentInPPDB(form1, form2):
        result = scorer.paraphrase

    elif wordnetSimilarity(form1, form2) > scorer.related_threshold:
        result = scorer.related

    result *= matchScore
    result += contextPenalty*scorer.context_importance

    return result

loadPPDB()