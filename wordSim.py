import re
from config import *

################################################################################
def loadPPDB(ppdbFileName = 'Resources/ppdb-1.0-xxxl-lexical.extended.synonyms.uniquepairs'):

    global synonymSimilarity
    global paraphraseSimilarity
    global ppdbDict

    count = 0
    
    ppdbFile = open(ppdbFileName, 'r')
    for line in ppdbFile:
        if line == '\n':
            continue
        tokens = line.split()
        tokens[1] = tokens[1].strip()
        ppdbDict[(tokens[0], tokens[1])] = paraphraseSimilarity
        count += 1

################################################################################


################################################################################
def presentInPPDB(word1, word2):

    global ppdbDict

    if (word1.lower(), word2.lower()) in ppdbDict:
        return True
    if (word2.lower(), word1.lower()) in ppdbDict:
        return True
    
################################################################################


##############################################################################################################################
def wordRelatedness(word1, pos1, word2, pos2):
    global stemmer
    global synonymSimilarity
    global paraphraseSimilarity
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
        return 1

    if stemmer.stem(word1).lower() == stemmer.stem(word2).lower():
        return 1

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

    word1Cleaned = re.sub(r'u\'(.+)\'', r'\1', word1).lower()
    word2Cleaned = re.sub(r'u\'(.+)\'', r'\1', word2).lower()

    ## use synonymDictionary or ppDB
    if synonymDictionary.checkSynonymByLemma(word1Cleaned, word2Cleaned):
        return synonymSimilarity
    elif presentInPPDB(word1Cleaned, word2Cleaned):
        return paraphraseSimilarity
    else:
       return 0

##############################################################################################################################
def functionWord(word):
    global punctuations

    return (word[2].lower() in stopwords) or (word[2].lower() in punctuations)

def weightedWordRelatedness(word1, word2, exact, stem, synonym, paraphrase, contextSimilarity):
    global stemmer
    global synonymSimilarity
    global paraphraseSimilarity
    global punctuations

    result = 0

    if len(word1[2]) > 1:
        canonicalWord1 = word1[2].replace('.', '')
        canonicalWord1 = canonicalWord1.replace('-', '')
        canonicalWord1 = canonicalWord1.replace(',', '')
    else:
        canonicalWord1 = word1[2]

    if len(word2[2]) > 1:
        canonicalWord2 = word2[2].replace('.', '')
        canonicalWord2 = canonicalWord2.replace('-', '')
        canonicalWord2 = canonicalWord2.replace(',', '')
    else:
        canonicalWord2 = word2[2]


    if canonicalWord1.lower() == canonicalWord2.lower():
        result = exact

    if word1[3].lower() == word2[3].lower() and result == 0:
        result = stem

    if stemmer.stem(word1[2]).lower() == stemmer.stem(word2[2]).lower() and result == 0:
        result = stem

    word1Cleaned = re.sub(r'u\'(.+)\'', r'\1', word1[3]).lower()
    word2Cleaned = re.sub(r'u\'(.+)\'', r'\1', word2[3]).lower()


    ## use synonymDictionary and ppDB

    if synonymDictionary.checkSynonymByLemma(word1Cleaned, word2Cleaned) and result == 0:
      result = synonym

    if presentInPPDB(word1Cleaned, word2Cleaned) and result == 0:
      result = paraphrase

    ## use contextSimilarity to calculate match score
    result += result * contextSimilarity / 5.0

    # result *= (contextSimilarity+1.0)/5.0

    return result

loadPPDB()