import re


def normalize(path):
    with open(path, 'r') as text:
        string = text.read()
        with open(path, 'w') as to_write:
            string = re.sub('\.', '. ', string)
            string = re.sub(' +', ' ', string)
            to_write.write(string)
            print('Normalized file %s' % path)


#paths = get_filepaths('/root/term_paper_2/ac_corpus')

#for path in paths:
#    normalize(path)




