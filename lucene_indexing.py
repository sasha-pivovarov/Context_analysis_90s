# -*- coding: utf-8 -*-
import lucene
lucene.initVM()
from lupyne import engine
from bs4 import BeautifulSoup
import bs4
from general_utility import ACIndex
import datetime
import re
import nltk
from nltk.stem.snowball import SnowballStemmer
from collections import OrderedDict
import general_utility as gu

stopwords = nltk.corpus.stopwords.words('russian')
stemmer = SnowballStemmer('russian')
tokenizer = nltk.RegexpTokenizer(ur'[^A-Ba-b\s\.\",:;\(\)\!\?]+') #WTF van Rossum?
corpus_index = ACIndex()
paths = gu.get_filepaths('/root/PycharmProjects/CA3/new_meta')
indexer = engine.Indexer('./lucene_index_05')
indexer.set('title', stored=True)
indexer.set('text', stored=True)
indexer.set('stemmed_text', stored=True)
indexer.set('rubrics', stored=True)
indexer.set('objects', stored=True)
indexer.set('metadata', stored=True)
indexer.set('keywords', stored=True)
indexer.set('id', stored=True)
indexer.set('mentions', stored=True)
indexer.set('path', stored=True, tokenized=False)


def normalize_date(date):
    if re.search('-', date):
        beginning, end = date.split('-')
        dates = []
        for number in beginning, end:
            day, month, year = [int(x) for x in number.split('.')]
            dates.append(datetime.date(year, month, day))
        return dates
    else:
        day, month, year = [int(x) for x in date.split('.')]
        return [datetime.date(year, month, day)]


def find_objects(soup):
    try:
        essences = soup.find_all('essence')
        #print(essences)
        enamexes = [tag for tag in soup.find_all('enamex') if
                    tag.has_attr('essn')]
        #print(enamexes)
        unordered_objects = {tag['name']: 0 for tag in essences}
        objects = OrderedDict(unordered_objects.items())
        for essence_tag in essences:

            for enamex_tag in enamexes:
                if enamex_tag['essn'] == essence_tag['number']:
                    objects[essence_tag['name']] += 1

            if essence_tag.has_attr('location'):
                for essence_tag2 in essences:
                    if essence_tag2['number'] == essence_tag['location']:
                        objects[essence_tag2['name']] += objects[essence_tag['name']]
            elif essence_tag.has_attr('person'):
                for essence_tag2 in essences:
                    if essence_tag2['number'] == essence_tag['person']:
                        objects[essence_tag2['name']] += objects[essence_tag['name']]
            elif essence_tag.has_attr('organization'):
                for essence_tag2 in essences:
                    if essence_tag2['number'] == essence_tag['organization']:
                        objects[essence_tag2['name']] += objects[essence_tag['name']]
            elif essence_tag.has_attr('unknown'):
                for essence_tag2 in essences:
                    if essence_tag2['number'] == essence_tag['unknown']:
                        objects[essence_tag2['name']] += objects[essence_tag['name']]
        #for key in objects:
            #assert objects[key] != 0




    except KeyError:
        objects = {'Нет данных' : 'Нет данных'}
    try:
        keywords = [tag['name'] for tag in soup.find_all('keyword')]
    except KeyError:
        keywords = ['Нет данных']
    try:
        rubrics = [tag['name'] for tag in soup.find_all('rubric')]
    except KeyError:
        rubrics = ['Нет данных']

    return objects, keywords, rubrics


def arrange_for_printing(array):

    to_write = []
    for tag in array:
        if type(tag) == bs4.element.Tag:
            if tag.has_attr('type'):
                if tag['type'] == 'DATE':
                    if datetime.date(1990,1,1) <= normalize_date(tag['norm'])[0] <= datetime.date(1999,12,31):
                        tag.string = 'ЦЕЛЕВАЯДАТА'
                    else:
                        tag.string = 'ДРУГАЯДАТА'

        try:
            to_write.append(tag.string)
        except AttributeError:
            to_write.append(arrange_for_printing(tag.contents))

    return to_write

def tokenize_and_stem(text, stem=True):
    tokens = tokenizer.tokenize(unicode(text))

    filtered_tokens = []
    for token in tokens:
        if token not in stopwords:
            filtered_tokens.append(token)
    if stem:
        stems = [stemmer.stem(t) for t in filtered_tokens]
        filtered_stems = []
        for stem in stems:
            if stem not in stopwords:
                filtered_stems.append(stem)
        return filtered_stems
    else:
        return filtered_tokens

def create_string(tags):
    string = ''
    for tag in tags:
        #tag = re.sub('<.*?>', '', tag)
        if tag.endswith('.') or tag.endswith('!') or tag.endswith('?') \
                or tag.endswith(u'ДРУГАЯДАТА') or tag.endswith(u'ЦЕЛЕВАЯДАТА') or tag.endswith('\n'):
            string += (tag + ' ')
        else:
            string += tag

    return string

def process_file_text(path):
    with open(path, 'r') as file:
        print(path)
        input_file_soup = BeautifulSoup(file, 'lxml')
        objects_with_mentions, keywords, rubrics = find_objects(input_file_soup)

        objects = '|||'.join(objects_with_mentions.keys())
        mentions = '|||'.join([str(x) for x in objects_with_mentions.values()])
        assert 0 not in objects.split('|||')

        keywords = '|||'.join(keywords)
        rubrics = '|||'.join(rubrics)
        test_tags_text = input_file_soup.find_all('s', t=['s','h'])
        test_tags_text = [x.contents for x in test_tags_text]
        test_tags_text = [j for i in test_tags_text for j in i]
        #print(test_tags_text)
        text_list = arrange_for_printing(test_tags_text)
        final_text = re.sub('<.*?>', '', create_string(text_list))
        stemmed_text = ' '.join(tokenize_and_stem(final_text))
        #print(final_text)
        #print(stemmed_text)


        prop_list = process_file_metadata(input_file_soup)

        print('Processed a text')
        # print(final_text)
        return final_text, rubrics, objects, prop_list, stemmed_text, keywords, path, mentions

def process_file_metadata(input_file_soup):
    prop_list = {'title': input_file_soup.find('prop', attrs={'name': 'head'}),
                 'author': input_file_soup.find('prop', attrs={'name': 'auth'}),
                 'date': input_file_soup.find('prop', attrs={'name': 'date'}),
                 'length': input_file_soup.find('prop', attrs={'name': 'tsize'}),
                 'rubric': input_file_soup.find('prop', attrs={'name': 'rubr'}),
                 'issue': input_file_soup.find('prop', attrs={'name': 'issue'}),
                 'url': input_file_soup.find('prop', attrs={'name': 'orig'})}

    for key in prop_list:
        if prop_list[key] is not None:
            prop_list[key] = prop_list[key].string
        else:
            prop_list[key] = 'Нет данных'
    #print(prop_list)
    return prop_list
idnum = 63856
def fill_index(path):
    global filtered, idnum
    props = process_file_text(path)
    if not re.search('---', props[0]):
        indexer.add(text=props[0], title=props[3]['title'], metadata=repr(props[3]),
                    rubrics=props[1], objects=props[2], stemmed_text=props[4], keywords=props[5], id=str(idnum),
                    path=props[6], mentions=props[7])
        idnum += 1
        print('Added entry #{}'.format(str(idnum)))
        #print(props[2])
        #print(props[7])
    else:
        filtered += 1
        print('Filtered out a table:')
        print(props[0])

filtered = 0
for path in paths:
    fill_index(path)

print(filtered)
indexer.commit()

# for x in range(idnum, 149662):
#     file = indexer.search('id:{}'.format(x))
#     assert len(file) == 1
#     print('Deleting file with id {}'.format(file[0]['id']))
#     indexer.delete('id:{}'.format(x))

