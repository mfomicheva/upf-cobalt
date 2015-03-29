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


def wordRelatedness(word1, pos1, word2, pos2, config):
    global stemmer
    global punctuations

    canonical_word1 = canonize_word(word1)
    canonical_word2 = canonize_word(word2)

    if canonical_word1 == canonical_word2:
        return config.exact

    if stemmer.stem(canonical_word1) == stemmer.stem(canonical_word2):
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

    if synonymDictionary.checkSynonymByLemma(word1, word2):
        return config.synonym

    elif presentInPPDB(word1, word2):
        return config.paraphrase

    elif wordnetSimilarity(word1, word2) > config.related_threshold:
        return config.related

    else:
        return 0


def maxWeightedWordRelatedness(word1, word2, scorer, contextPenalty):
    relatedness = max(weightedWordRelatedness(word1.form, word2.form, word1, word2, scorer, contextPenalty, scorer.exact),
                      weightedWordRelatedness(word1.lemma, word2.lemma, word1, word2, scorer, contextPenalty, scorer.stem))

    return max(relatedness, scorer.minimal_aligned_relatedness)


def weightedWordRelatedness(form1, form2, word1, word2, scorer, contextPenalty, matchScore):
    global stemmer
    global punctuations

    result = 0

    canonical_word1 = canonize_word(form1)
    canonical_word2 = canonize_word(form2)

    if canonical_word1 == canonical_word2:
        result = scorer.exact

    elif contractionDictionary.check_contraction(canonical_word1, canonical_word2):
        result = scorer.exact

    elif stemmer.stem(canonical_word1) == stemmer.stem(canonical_word2):
        result = scorer.stem

    elif synonymDictionary.checkSynonymByLemma(form1, form2):
        result = scorer.synonym

    elif presentInPPDB(form1, form2):
        result = scorer.paraphrase

    #elif not functionWord(word1) and not functionWord(word2) and \
    #        wordnetSimilarity(form1, form2) > scorer.related_threshold:
    #    result = scorer.related

    result *= matchScore
    result += contextPenalty*scorer.context_importance

    return result

loadPPDB()