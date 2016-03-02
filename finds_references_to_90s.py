import nltk
import json
import pymorphy2


morph = pymorphy2.MorphAnalyzer()
paths = json.load(open('/root/term_paper_2/ac_corpus_index/allpaths.json'))
lexeme =  morph.parse("девяностые")[0].lexeme
ninetyforms = [x.word for x in lexeme if 'plur' in x.tag]
ninetyforms.extend(['1990-х', '1990-е', '1990-ым', '1990-ыми', '1990-ые', '1990-ых', '90-e', '90-х', '90-ые', '90-ым', '90-ыми', '90-ых'])
ninetyforms = set(ninetyforms)
ninetypaths = []

for path in paths:
    file = open(path, 'r')
    #print(path)
    string = file.read()
    tokens = nltk.word_tokenize(string)
    intersection = ninetyforms.intersection({word.lower() for word in tokens})
    if intersection:
        ninetypaths.append(path)
        print('appended file %s with intersection %s' % (path, repr(intersection)))

print(ninetypaths)
print(len(ninetypaths))
json.dump(ninetypaths, open('/root/term_paper_2/ac_corpus_index/ninetypaths.json', 'w'), ensure_ascii=False)