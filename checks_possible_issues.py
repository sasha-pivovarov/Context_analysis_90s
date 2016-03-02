import creates_xml as cx
import os
from bs4 import BeautifulSoup
import json

subdirs = cx.get_immediate_subdirectories('/root/term_paper_2/articles')
list_dirs = ['/root/term_paper_2/articles/' + x + '/Meta' for x in subdirs]
number = 0
check_results = []
for dir in list_dirs:
    for file in os.listdir(dir):

        to_check = open(dir + '/' + file)
        soup = BeautifulSoup(to_check)
        to_check.close()
        checktag = soup.find('prop', attrs={'name': 'issue'})

        if checktag is not None:
            checktag = checktag.string
        else:
            check_results.append('No title in %s' % dir + '/' + file)

        if checktag not in check_results:
            check_results.append(checktag)
        number += 1
        print(number)


json.dump(check_results, open('/root/term_paper_2/articles/issues.json', 'w'), ensure_ascii=False)
print(check_results)