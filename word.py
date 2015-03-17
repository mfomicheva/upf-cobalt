class Word(object):

    index = -1

    form = None

    lemma = None

    pos = None

    def __init__(self, index, form, lemma, pos):
        self.index = index
        self.form = form
        self.lemma = lemma
        self.pos = pos


