import json, jsonpickle
from bs4 import BeautifulSoup
import nltk
import pymorphy2


with open('/root/term_paper_2/ac_corpus_index/ninetypaths.json', 'r') as file:
    filepaths = json.load(file)
# filepaths = ["/root/term_paper_2/ac_corpus/Ведомости/2013/Ведомости_2013_36"]
ninetyforms = jsonpickle.decode(open('/root/term_paper_2/ac_corpus_index/ninetyforms.json', 'r').read())


class Collocator:
    def __init__(self, inrange):
        self.range = inrange
        self.dicts = [{} for x in range(-inrange, inrange+1)]

    def collocate(self, paths, startwords, morphanalyzer=pymorphy2.MorphAnalyzer()):
        for path in paths:
            with open(path, 'r') as file:
                soup = BeautifulSoup(file, 'xml')
            text = soup.p.string
            tokens = nltk.RegexpTokenizer(r'\w+-*\w*').tokenize(text)
            cleantokens = [word.lower() for word in tokens if morphanalyzer.parse(word)[0].tag.POS
                           not in {'PREP', 'CONJ', 'PRCL', 'NPRO' } and 'Apro' not in morphanalyzer.parse(word)[0].tag and
                           'Dmns' not in morphanalyzer.parse(word)[0].tag]
            tokenset = set(tokens)
            for word in tokenset.intersection(startwords):
                index = cleantokens.index(word)
                for value in range(-self.range, self.range+1):
                    try:
                        if morphanalyzer.parse(cleantokens[index + value])[0].normal_form \
                                not in self.dicts[value+self.range].keys():
                            self.dicts[value + self.range][morphanalyzer.parse(
                                    cleantokens[index + value])[0].normal_form] = 1
                        else:
                            self.dicts[value + self.range][morphanalyzer.parse(
                                    cleantokens[index + value])[0].normal_form] += 1
                    except IndexError:
                        pass

    def request(self, position='all'):
        if position != 'all':
            try:
                return sorted(self.dicts[self.range+position], key=self.dicts[self.range+position].get)
            except IndexError:
                return 'Position %s not present in this collocation' % position
        else:
            for dict in self.dicts:
                yield sorted(dict, key=dict.get)


fourcolloc = Collocator(4)
fourcolloc.collocate(filepaths, ninetyforms)
dumpstring = jsonpickle.encode(fourcolloc)
with open('/root/term_paper_2/ac_corpus_data/collocator_4.json', 'w') as file:
    file.write(dumpstring)

print(fourcolloc.dicts)
print(ninetyforms)
hfreqarray_15 = []
for array in fourcolloc.request():
    print(array[-15:])
    hfreqarray_15.append(array[-15:])
json.dump(hfreqarray_15, open('/root/term_paper_2/ac_corpus_data/hfreq15.json', 'w'), ensure_ascii=False)
