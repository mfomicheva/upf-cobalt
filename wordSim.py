import re
from config import *

################################################################################
def loadPPDB(ppdbFileName = 'Resources/ppdb-1.0-xxxl-lexical.extended.synonyms.uniquepairs'):

    global synonymSimilarity
    global ppdbDict

    count = 0
    
    ppdbFile = open(ppdbFileName, 'r')
    for line in ppdbFile:
        if line == '\n':
            continue
        tokens = line.split()
        tokens[1] = tokens[1].strip()
        ppdbDict[(tokens[0], tokens[1])] = synonymSimilarity
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
    word1 = word1.decode('UTF-8')
    word2 = word2.decode('UTF-8')

    global stemmer
    global synonymSimilarity
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

    if synonymDictionary.checkSynonymByLemma(word1Cleaned, word2Cleaned):
    #if presentInPPDB(word1Cleaned, word2Cleaned):
        return synonymSimilarity
    else:
        return 0
##############################################################################################################################
def functionWord(word):
    global punctuations

    return (word[2].lower() in stopwords) or (word[2].lower() in punctuations)

def weightedWordRelatedness(word1, word2, exact, stem, synonym):
    #word1[2] = word1[2].decode('UTF-8')
    #word2[2] = word2[2].decode('UTF-8')

    global stemmer
    global synonymSimilarity
    global punctuations

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
        return exact

    if word1[3].lower() == word2[3].lower():
        return stem

    if stemmer.stem(word1[2]).lower() == stemmer.stem(word2[2]).lower():
        return stem

    if canonicalWord1.isdigit() and canonicalWord2.isdigit() and canonicalWord1 <> canonicalWord2:
        return 0

    if word1[4].lower() == 'cd' and word2[4].lower() == 'cd' and (not canonicalWord1.isdigit() and not canonicalWord2.isdigit()) and canonicalWord1 <> canonicalWord2:
        return 0

    # stopwords can be similar to only stopwords
    if (word1[2].lower() in stopwords and word2[2].lower() not in stopwords) or (word1[2].lower() not in stopwords and word2[2].lower() in stopwords):
        return 0

    # punctuations can only be either identical or totally dissimilar
    if word1[2] in punctuations or word2[2] in punctuations:
        return 0

    word1Cleaned = re.sub(r'u\'(.+)\'', r'\1', word1[3]).lower()
    word2Cleaned = re.sub(r'u\'(.+)\'', r'\1', word2[3]).lower()
    if synonymDictionary.checkSynonymByLemma(word1Cleaned, word2Cleaned):
        return synonym
    else:
        return 0

loadPPDB()

