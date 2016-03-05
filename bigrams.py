"""This is an impressively terrible solution. I should redo this ASAP;
NLTK probably has the means to extract bigrams from an entire corpus instead of just one text.
"""


import nltk
import pymorphy2
import json, jsonpickle

#paths = json.load(open('/root/term_paper_2/ac_corpus_index/ninetypaths.json', 'r'))
forms = jsonpickle.decode(open('/root/term_paper_2/ac_corpus_index/ninetyforms.json', 'r').read())
longstring = open('/root/term_paper_2/ac_corpus_data/longstring_90.txt', 'r').read()
morph = pymorphy2.MorphAnalyzer()
filter_tags = {}

longstring_tokens = nltk.RegexpTokenizer(r'\w+-*\w*').tokenize(longstring)
longtext = nltk.Text(longstring_tokens)

bigram_measures = nltk.collocations.BigramAssocMeasures()


finder = nltk.BigramCollocationFinder.from_words(longtext)
finder.apply_freq_filter(5)
finder.apply_ngram_filter(lambda w1, w2: forms.intersection({w1, w2}) == set())
finder.apply_ngram_filter(lambda w1, w2: morph.parse(w1)[0].tag.POS in {'PREP', 'CONJ', 'PRCL', 'NPRO' } or 'Apro' in morph.parse(w1)[0].tag or
                           'Dmns' in morph.parse(w1)[0].tag or morph.parse(w2)[0].tag.POS in
                            {'PREP', 'CONJ', 'PRCL', 'NPRO' } or 'Apro' in morph.parse(w2)[0].tag or 'Dmns' in morph.parse(w2)[0].tag)


print(finder.nbest(bigram_measures.likelihood_ratio, 300))
print(len(finder.nbest(bigram_measures.likelihood_ratio, 300)))

