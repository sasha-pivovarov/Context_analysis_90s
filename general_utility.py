import json
import jsonpickle
import pymorphy2
import os

def get_subdirectories(a_dir):
    return [dirpath for dirpath, dirnames, filenames in os.walk(a_dir)]


def get_filepaths(a_dir):
    dirs = get_subdirectories(a_dir)
    filenames = []
    for dir in dirs:
        filenames.extend([(dir + '/' + path) for path in os.listdir(dir) if os.path.isfile(dir + '/' + path)])

    return filenames


def pathdump(dirpath, file):
    """This will dump the results into a .json file
    """
    paths =  get_filepaths(dirpath)  #['/root/term_paper_2/ac_corpus/Ведомости/2014/Ведомости_2014_1']
    json.dump(paths, open(file, 'w'), ensure_ascii=False)


def formdump():
    morph = pymorphy2.MorphAnalyzer()
    lexeme = morph.parse("девяностые")[0].lexeme
    ninetyforms = [x.word for x in lexeme if 'plur' in x.tag]
    ninetyforms.extend(['1990-х', '1990-е', '1990-ым', '1990-ыми', '1990-ые', '1990-ых',
                        '90-e', '90-х', '90-ые', '90-ым', '90-ыми', '90-ых'])
    ninetyforms = set(ninetyforms)
    jsonstring_ninetyforms = jsonpickle.encode(ninetyforms)
    with open('/root/term_paper_2/ac_corpus_index/ninetyforms.json', 'w') as file:
        file.write(jsonstring_ninetyforms)
