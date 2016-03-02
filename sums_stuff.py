import json
number = json.load(open('/root/term_paper_2/articles/numbers.json', 'r'))


for key, value in number.items():
    total = 0
    for value2 in value.values():
        total += int(value2)
    print(key, ' is ', total)
    number[key][key + 'total'] = total

json.dump(number, open('/root/term_paper_2/articles/numbers.json', 'w'), ensure_ascii=False)
