from bs4 import BeautifulSoup
import json
import os
import string

def arrange_for_printing(array):

    to_write = []
    for tag in array:
        try:
            to_write.append(tag.string)
        except AttributeError:
            to_write.append(arrange_for_printing(tag.contents))

    return to_write


def process_file_text(input_file_soup):

    test_tags_text = input_file_soup.find_all('s', t=['s','h'])
    test_tags_text = [x.contents for x in test_tags_text]
    test_tags_text = [j for i in test_tags_text for j in i]
    text_list = arrange_for_printing(test_tags_text)
    final_text = ''.join(text_list)
    #print(final_text)
    return final_text


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


def create_new_soup(blank_soup, text, props):

    blank_soup.URL.string = props['url']
    blank_soup.SOURCE.string = props['issue']
    blank_soup.RUBRIC.string = props['rubric']
    blank_soup.WORDCOUNT.string = str(len(text.split()))
    blank_soup.DATE.string = props['date']
    blank_soup.AUTHOR.string = props['author']
    blank_soup.TITLE.string = props['title']
    blank_soup.p.string = text

    return blank_soup


def create_name_and_write(blank_soup, props):

    global number
    issue_standin = props['issue']
    if props['issue'] not in ['Ведомости', 'Коммерсантъ', 'Аргументы и Факты', 'Комсомольская правда']:
        if props['issue'].startswith('Аргументы и Факты'):
            issue_standin = 'Аргументы и Факты'
        elif props['issue'].startswith('Ведомости'):
            issue_standin = 'Ведомости'
        elif props['issue'].startswith('Коммерсантъ'):
            issue_standin = 'Коммерсантъ'
        elif props['issue'].lower().startswith('комсомольская правда'):
            issue_standin = 'Комсомольская правда'
        else:
            print('Failed to write file with issue: %s' % props['issue'])
            return None


    if len(blank_soup.p.string) == 0:
        print('Failed to write file due to null wordcount')
        return None

    filename = '/root/term_paper_2/ac_corpus/%s/%s/%s' % (issue_standin, props['date'][:4], issue_standin + '_' + props['date'][:4]
                                                              + '_' + str(number[issue_standin][props['date'][:4]]))

    print(filename)

    number[issue_standin][props['date'][:4]] += 1
    number[issue_standin]['total'] += 1

    to_write = open(filename, 'w')
    to_write.write(blank_soup.prettify())
    print('wrote filename %s' % filename)
    to_write.close()


def get_subdirectories(a_dir):
    return [dirpath for dirpath, dirnames, filenames in os.walk(a_dir)]


def make_folders(dirs):
    for dir in dirs:
        for i in range(2000, 2016):
            if not os.path.exists(dir + '/' + str(i)):
                os.mkdir('/root/term_paper_2/ac_corpus/' + dir + '/' + str(i))


# number = {
#     'Ведомости': {i: 0 for i in range(2000, 2016)},
#     'Коммерсантъ': {i: 0 for i in range(2000, 2016)},
#     'Аргументы и Факты': {i: 0 for i in range(2000, 2016)},
# }

number = json.load(open('/root/term_paper_2/articles/numbers.json', 'r'))

number['Комсомольская правда'] = {str(i): 0 for i in range(2000, 2016)}
number['Комсомольская правда']['total'] = 0


failures = []

blank_file = open('/root/term_paper_2/xml_blank')
blank_soup = BeautifulSoup(blank_file, 'xml')

# subdirs = get_immediate_subdirectories('/root/term_paper_2/articles')
# list_dirs = ['/root/term_paper_2/articles/' + x + '/Meta' for x in subdirs]

dir = input('Input root directory path: ')#'/root/term_paper_2/articles/QRet-2015-12-11-04-35-38/Meta'



for file in os.listdir(dir):
    work_file = open(dir + '/' + file, 'r')
    work_soup = BeautifulSoup(work_file)
    work_file.close()
    try:
        final_text = process_file_text(work_soup)
        metadata = process_file_metadata(work_soup)
        new_soup = create_new_soup(blank_soup, final_text, metadata)
        create_name_and_write(new_soup, metadata)
    except:
        failures.append(dir + '/' + file)
        print('Failed to process file %s' % file)

json.dump(number, open('/root/term_paper_2/articles/numbers.json', 'w'), ensure_ascii=False)
print(len(failures))
failure_list = open('/root/term_paper_2/articles/failures.txt', 'a')
for failure in failures:
    failure_list.write(failure + '\n')
failure_list.close()
blank_file.close()

