# -*- coding: utf-8 -*-

import json
# import jsonpickle
# import pymorphy2
import os
from bs4 import BeautifulSoup
import re

def get_subdirectories(a_dir):
    return [dirpath for dirpath, dirnames, filenames in os.walk(a_dir)]


def get_filepaths(a_dir, extension=0):
    dirs = get_subdirectories(a_dir)
    filenames = []
    if not extension:
        for dir in dirs:
            filenames.extend([(dir + '/' + path) for path in os.listdir(dir) if os.path.isfile(dir + '/' + path)])
    else:
        for dir in dirs:
            filenames.extend([(dir + '/' + path) for path in os.listdir(dir) if os.path.isfile(dir + '/' + path) and path.endswith(extension)])

    return filenames


def pathdump(dirpath, file, extension=0):
    """This will dump the results into a .json file
    """
    paths =  get_filepaths(dirpath, extension)  #['/root/term_paper_2/ac_corpus/Ведомости/2014/Ведомости_2014_1']
    json.dump(paths, open(file, 'w'), ensure_ascii=False)


# def formdump():
#     morph = pymorphy2.MorphAnalyzer()
#     lexeme = morph.parse("девяностые")[0].lexeme
#     ninetyforms = [x.word for x in lexeme if 'plur' in x.tag]
#     ninetyforms.extend(['1990-х', '1990-е', '1990-ым', '1990-ыми', '1990-ые', '1990-ых',
#                         '90-e', '90-х', '90-ые', '90-ым', '90-ыми', '90-ых'])
#     ninetyforms = set(ninetyforms)
#     jsonstring_ninetyforms = jsonpickle.encode(ninetyforms)
#     with open('/root/term_paper_2/ac_corpus_index/ninetyforms.json', 'w') as file:
#         file.write(jsonstring_ninetyforms)


def stringdump(paths):
    longstring = ''
    for path in paths:
        with open(path, 'r') as file:
            string = BeautifulSoup(file).p.string
        longstring += ('\n' + string)

    with open('/root/term_paper_2/ac_corpus_data/longstring_90.txt', 'w') as file:
        file.write(longstring)


def remove_brackets_from_string(string):
    return re.sub('<.*?>', ' ', string)

def just_strings():
    for path in json.load(open('/root/term_paper_2/ac_corpus_index/allpaths.json', 'r')):
        with open(path, 'r') as file:
            string = BeautifulSoup(file).p.string
            filename = '/root/term_paper_2/ac_corpus_data/just_strings/%s' % path.split('/')[-1]
            with open(filename, 'w') as writefile:
                writefile.write(string)

class ACIndex:
    def __init__(self):
        self.all_paths = json.load(open('/root/term_paper_2/ac_corpus_index/allpaths.json', 'r'))
        self.string_paths = json.load(open('/root/term_paper_2/ac_corpus_index/stringpaths.json', 'r'))
        self.sample_paths = json.load(open('/root/term_paper_2/ac_corpus_index/sample_articles.json', 'r'))
        self.nineties_mention_paths = json.load(open('/root/term_paper_2/ac_corpus_index/ninetypaths.json', 'r'))
        self.meta_paths = json.load(open('/root/term_paper_2/ac_corpus_index/metapaths.json', 'r'))

class NewIndex:
    def __init__(self):
        self.all_paths = json.load(open('/home/anna/PycharmProjects/CA3/ac_corpus/ac_corpus_index/newpaths.json'))
        self.meta_paths = json.load(open('/home/anna/PycharmProjects/CA3/ac_corpus/ac_corpus_index/metapaths.json'))
        self.model_paths = json.load(open('/home/anna/PycharmProjects/CA3/ac_corpus/ac_corpus_index/model_paths.json'))





