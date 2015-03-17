from scorer import Scorer
from synonymDictionary import SynonymDictionary

ppdbDict = {}
theta1 = 0.9

from nltk.corpus import stopwords
from nltk import SnowballStemmer


stemmer = SnowballStemmer('english')
synonymDictionary = SynonymDictionary('english')

punctuations = ['(','-lrb-','.',',','-','?','!',';','_',':','{','}','[','/',']','...','"','\'',')', '-rrb-']
punctuations = map(lambda x: x.encode('UTF-8'), punctuations)

stopwords = stopwords.words('english')
stopwords = map(lambda x: x.encode('UTF-8'), stopwords)
