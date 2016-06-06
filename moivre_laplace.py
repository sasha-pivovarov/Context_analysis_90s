# -*- coding: utf-8 -*-
import lucene
lucene.initVM()
from lupyne import engine
import operator
import codecs
import nltk
import pickle
import math as m
import json
import re
from nltk.collocations import *
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import csv
from networkx.readwrite import json_graph


stopwords = nltk.corpus.stopwords.words('russian')


tokenizer = nltk.RegexpTokenizer(ur'[^A-Ba-b\s\.\",:;\(\)\!\?]+')

indexer = engine.Indexer('./lucene_index_05')
country_string = ' '.join([x for x in open('country_list.txt').read().split('\n')
                             if len(x.split()) < 2])
# print(country_string)
# print(type(country_string))
hits = indexer.search('stemmed_text:(целеваядат девян "90-е" "90-х" "90-ым") NOT objects:({})'.format(country_string))
reverse_first = indexer.search('(stemmed_text:(целеваядат девян "90-е" "90-х" "90-ым") AND objects:({})) OR (*:* AND NOT stemmed_text:(целеваядат девян "90-е" "90-х" "90-ым"))'.format(country_string))
all = indexer.search()
#print(len(hits))

assert len(hits) + len(reverse_first) == len(all)

decile_one_first = hits[:(len(hits)//5)]
deciles2_10_first = hits[(len(hits)//5):]

#decile_one = indexer.search('objects:Ельцин AND stemmed_text:(целеваядат девян "90-е" "90-х" "90-ым") NOT objects:({})'.format(country_string))

# print(len(decile_one))
# for hit in decile_one[:10]:
#     print(hit['title'])
#     print(hit['text'])
#     print(hit['objects'])
#     print(hit['mentions'])
#     print('\n')

# reverse = list(reverse_p[510:600])
# decile_one = list(decile_one[:10])
#
# reverse += decile_one[3:5]
# decile_one += reverse[55:57]


lbtc0 = [-0.6931471806, 0.7978845605, -0.3183098861, 0.0363356023, 0.00478211176,
        -0.000036980745, -0.0002120257200, -0.0000521599987, -0.161680983E-5, 0.2851334009E-5]
lbtc1 = [ -53.23128515, 10.09809323, -0.4952773111, 0.0002977333987,
          0.00002074390927, 0.1514595081e-5, 0.1131629551e-6, 0.8540593192e-8, 0.6458507274e-9, 0.4865830484e-10]
lbtc2 = [-203.9171554, 20.04975307, -0.4987683692, 0.00004045442982, 0.1487647983e-5,
         0.5807156793e-7, 0.2349932467e-8]
lbtc3 = [-454.3212440, 30.03325967, -0.4994481142, 0.00001218332169, 0.3019140505e-6,
         0.7963045815e-8, 0.2182998026e-9]


def find_L(hits_object):
    L = 0
    for hit in hits_object:
        L += len(tokenizer.tokenize(unicode(hit['text'])))
        print('Calculating L...')

    print('Found L: %d' % L)
    return L

def find_objects(hits_object, dump_path=None):
    objects = []
    for hit in hits_object:
        try:
            objects.extend(hit['objects'].split('|||'))
        except AttributeError:
            print('No objects in this text:')
            print(hit['text'])
    object_set = set(objects)

    if dump_path:
        with open(dump_path, 'w') as dump_file:
            pickle.dump(object_set, dump_file)

    print('Found %d objects' % len(object_set))
    return object_set


def get_object_dictionary(hits_obj, add_null_objects=False, dump_path=None,
                          punish_singletext=None, punish_length=False, kill=0):
    object_dict = {}
    for hit in hits_obj:
        try:
            objects = hit['objects'].split('|||')
            mentions = [int(x.strip()) for x in hit['mentions'].split('|||')]
            try:
                length = len(tokenizer.tokenize(hit['text']))
            except TypeError:
                length = 4000
            if punish_length:
                if length > 1000:
                    mentions = [x * (float(1000) / length) for x in mentions]

        except AttributeError:
            print('WTH was this just now:')
            print(hit['title'])
            print(hit['text'])
            objects = []
            mentions =[]
        except UnicodeEncodeError:
            print(hit['mentions'])
            print('NO OBJECT DATA')
            objects = []
            mentions = []
        for object in objects:
            if re.search(';', object):
                # print('EXTENDING, PREVIOUS STATE:')
                # print('|||'.join(objects))
                # print('|||'.join([str(x) for x in mentions]))

                temps = [x.split(';') for x in object.split()]
                #assert len(temps) < 3
                new_objs = []
                if len(temps) == 2:
                    for obj1 in temps[0]:
                        for obj2 in temps[1]:
                            new_objs.append(u'{} {}'.format(obj2, obj1))
                elif len(temps) == 1:
                    new_objs = [x for x in temps[0]]
                else:
                    break
                new_ments = [mentions[objects.index(object)] for x in new_objs]
                del mentions[objects.index(object)]
                objects.remove(object)
                mentions.extend(new_ments)
                objects.extend(new_objs)
                # print('NEW STATE:')
                # print('|||'.join(objects))
                # print('|||'.join([str(x) for x in mentions]))

        if len(mentions) == len(objects):
            for object in objects:
                if object not in object_dict:
                    if mentions[objects.index(object)] != 0:
                        object_dict[object] = [mentions[objects.index(object)], 1]
                    else:
                        if add_null_objects:
                            object_dict[object] = [mentions[objects.index(object)], 1]
                else:
                    object_dict[object][0] += mentions[objects.index(object)] ; object_dict[object][1] += 1
            print('Added some objects.')
        else:
            print('The length thing again.')
    for object in object_dict:
        assert isinstance(object_dict[object][0], int) or isinstance(object_dict[object][0], float)
        if punish_singletext:
            if object_dict[object][1] == 1:
                object_dict[object][0] = float(object_dict[object][0]) / punish_singletext
        if kill:
            if object_dict[object][1] <= kill:
                del object_dict[object]
    if dump_path:
        with open(dump_path, 'w') as dump_file:
            pickle.dump(object_dict, dump_file)
    return object_dict


def get_objects_with_P(objdict_R, objdict_IR, L, dump_path = None):
    #objects_foruse = objdict_R.copy()
    objects_with_P = {}
    for object in objdict_R:
        if object in objdict_IR:
            objects_with_P[object] = float(objdict_R[object][0] + objdict_IR[object][0] + 1) / float(L)
        else:
            objects_with_P[object] = float(objdict_R[object][0] + 1) / float(L)

        #assert objdict_R[object] != 0
        #P = float(objdict_R[object]) / float(L)
    for object in objects_with_P:
        assert objects_with_P[object] != 0
        #objects_with_P[object] = P

    if dump_path:
        with open(dump_path, 'w') as dump_file:
            pickle.dump(objects_with_P, dump_file)

    print('Got Ps.')
    return objects_with_P

def log_binomial_tail_objs(objects_with_P, objdict_R, L, dump_path=None):
    objects_with_lbt = {}
    for object in objects_with_P:
        Nr = float(objdict_R[object][0])
        P = float(objects_with_P[object])
        assert Nr != 0
        assert L != 0
        assert P != 0
        #assert m.sqrt(L*P*(1-P)) != 0

        sigma_deviation = -((Nr - L * P) / m.sqrt((L*P*(1-P))))
        #print('Did {} - {} * {} / m.sqrt({} * {} * (1 - {}), got {}'.format(Nr, L, P, L, P, P, MLC))
        if sigma_deviation > 2:
            lbt = 0
        elif sigma_deviation >= -2:
            lbt = np.polyval(lbtc0, sigma_deviation)
        elif sigma_deviation >= -11:
            lbt = np.polyval(lbtc1, sigma_deviation)
        elif sigma_deviation >= -30:
            lbt = np.polyval(lbtc2, sigma_deviation)
        elif sigma_deviation >= -120:
            lbt = np.polyval(lbtc3, sigma_deviation)
        else:
            lbt = -10755.11947 + 124.0043967 * (sigma_deviation + 120)
        objects_with_lbt[object] = [lbt, -sigma_deviation]
    # for object in objects_with_lbt:
    #     assert objects_with_lbt[object] != 0
    if dump_path:
        with open(dump_path, 'w') as dump_file:
            pickle.dump(objects_with_lbt, dump_file)

    print('Got binomial tail logarithm scores.')

    return objects_with_lbt

# def get_lnerfs(moivre_laplace_objs, dump_path = None):
#     objs_with_lnerfs = {}
#     for object in moivre_laplace_objs:
#         #print(m.erf(moivre_laplace_objs[object]))
#         try:
#             lnerf = m.log(m.erf(moivre_laplace_objs[object]))
#         except ValueError:
#             lnerf = 1234.0
#         objs_with_lnerfs[object] = lnerf
#     if dump_path:
#         with open(dump_path, 'w') as dump_file:
#             pickle.dump(objs_with_lnerfs, dump_file)
#
#     print('Got lnerfs.')
#
#     return objs_with_lnerfs

def get_keywords(hits_object, dump_path=None, punish_singletext=None, punish_length=False, kill=0 ):
    keyword_dict = {}
    for hit in hits_object:
        try:
            keywords = hit['keywords'].split('|||')
        except AttributeError:
            keywords = []
            print('Skipped text with no keywords.')
        for keyword in keywords:
            try:
                words = tokenizer.tokenize(hit['text'])
                length = len(words)
            except TypeError:
                words = []
                length = 5000
            count = 1
            for word in words:
                if word[:6] == keyword[:6]:
                    count += 1
            if punish_length:
                if length > 1000:
                    count = count / (float(1000)/length)
            if keyword in keyword_dict:
                keyword_dict[keyword][0] += count ; keyword_dict[keyword][1] += 1
            else:
                keyword_dict[keyword] = [count, 1]
            print('Got a keyword')
    for key in keyword_dict:
        if punish_singletext:
            if keyword_dict[key][1] == 1:
                keyword_dict[key][0] = float(keyword_dict[key][0]) / punish_singletext
        if kill:
            if keyword_dict[key][1] <= kill:
                del keyword_dict[key]
    if dump_path:
        with open(dump_path, 'w') as dump_file:
            pickle.dump(keyword_dict, dump_file)

    return keyword_dict

def process_keyword_probabilities(keydict_R, keydict_IR, L, Lr, dump_path=None):
    keywords_p = {}
    for keyword in keydict_R:
        if keyword in keydict_IR:
            N = float(keydict_IR[keyword][0] + keydict_R[keyword][0] + 1)
        else:
            N = float(keydict_R[keyword][0] + 1)
        P = float(N) / L
        Nr = float(keydict_R[keyword][0])
        sigma_deviation = -((Nr - Lr *P) / (m.sqrt(Lr*P*(1-P))))
        if sigma_deviation > 2:
            lbt = 0
        elif sigma_deviation >= -2:
            lbt = np.polyval(lbtc0, sigma_deviation)
        elif sigma_deviation >= -11:
            lbt = np.polyval(lbtc1, sigma_deviation)
        elif sigma_deviation >= -30:
            lbt = np.polyval(lbtc2, sigma_deviation)
        elif sigma_deviation >= -120:
            lbt = np.polyval(lbtc3, sigma_deviation)
        else:
            lbt = -10755.11947 + 124.0043967 * (sigma_deviation + 120)

        keywords_p[keyword] = [lbt, -sigma_deviation]

    if dump_path:
        with open(dump_path, 'w') as dump_file:
            pickle.dump(keywords_p, dump_file)
    return keywords_p


def dumb_formula(decile_one, reverse, objdict_R, objdict_IR):
    scored_objects = {}

    for object, count in objdict_R.items():
        x = float(count[0])
        V = len(decile_one)
        if object in objdict_IR:
            x0 = float(objdict_IR[object][0]) + 1
        else:
            x0 = float(1)
        V0 = len(reverse)
        assert V0 != 0
        assert V != 0
        assert (x0/V0) != 0
        object_score = (x / V) / (x0 / V0)
        scored_objects[object] = int(round(object_score))

    sorted_objects = sorted(scored_objects.items(), key=operator.itemgetter(1))
    return sorted_objects


def show_by_quantile(n, number, hits_obj):
    quantile_range = len(hits_obj) // n

    initial_range = 0
    quantile_number = 1

    while initial_range < len(hits_obj):
        decile = hits_obj[initial_range:(initial_range + quantile_range)]
        print('\n-------------------------------\n')
        print('THOSE ARE THE TOP {} TEXTS FROM {}-quantile {}:\n'.format(str(number), str(n), str(quantile_number)))
        for hit in decile[:number]:
            print('-----------------')
            print(hit['title'])
            print('\n')
            print(hit['text'])

        initial_range += quantile_range
        quantile_number += 1

def write_sortedlist(path, items):
    with codecs.open(path, 'a', encoding='utf-8') as file:
        for tuple in items:
            file.write(tuple[0])
            file.write(' ')
            file.write(str(tuple[1]))
            file.write('\n')


def get_objects_by_prob_comp(objects_w_p, objdict_Nr, objdict_Nir, L_rel, L_ir, cut_infrequent=True, dump_path=None):
    objects_by_prob_comp = {}
    for object in objdict_Nr:
        Pr = float(objdict_Nr[object][0]) / float(L_rel)
        try:
            Pir = float(objdict_Nir[object][0]) / float(L_ir)
        except KeyError:
            Pir = 1 / float(L_ir)
        score = Pr / Pir
        if cut_infrequent:
            if objdict_Nr[object][1] <= 1:
                score = score / 4
        objects_by_prob_comp[object] = score
    if dump_path:
        with open(dump_path, 'w') as dump_file:
            pickle.dump(objects_by_prob_comp, dump_file)
    return objects_by_prob_comp

def get_words(hits_object):
    words = []
    for hit in hits_object:
        words.extend(tokenizer.tokenize(hit['text']))

    return words

def make_colloc_network(collocs):
    network = nx.Graph()
    for x, y in collocs:
        network.add_node(x)
        network.add_node(y)
        network.add_edge(x, y)
        print('Addded an edge.')

    return network


def do_iteration_1(decile_one, deciles2_10, reverse, dumpobj, dumpkey):

    dumpkeyfile = codecs.open(dumpkey, 'w', encoding='utf-8')
    dumpobjfile = codecs.open(dumpobj, 'w', encoding='utf-8')
    # L = find_L(all)
    # with open('length_all.pkl', 'w') as dump:
    #     pickle.dump(L, dump)
    L = pickle.load(open('length_all.pkl'))
    #Lr = find_L(decile_one)
    Lr = find_L(decile_one)
    #pickle.dump(Lr, open('length_relevant.pkl', 'w'))

    key_R = get_keywords(decile_one, dump_path='key_R_fixed.pkl')
    key_reverse = get_keywords(reverse, dump_path='key_reverse_fixed.pkl')
    key_2_10 = get_keywords(deciles2_10, dump_path='key_2_10_fixed.pkl')
    key_IR = {}
    # key_R = pickle.load(open('key_R_fin.pkl'))
    # key_IR = pickle.load(open('key_IR_fin.pkl'))

    for key in key_reverse:
        if key in key_2_10:
            key_IR[key] = (key_reverse[key][0] + key_2_10[key][0], key_reverse[key][1] + key_2_10[key][1])
        else:
            key_IR[key] = key_reverse[key]
    pickle.dump(key_IR, open('key_IR_fixed.pkl', 'w'))

    keyword_probs = process_keyword_probabilities(key_R, key_IR, L, Lr, 'key_probs_last.pkl')
    keys_sorted = sorted([(x, y[0]) for x,y in keyword_probs.items()], key=operator.itemgetter(1))

    for key, prob in keys_sorted:
        try:
            dumpkeyfile.write(key + ',' + str(prob) + ',' + str(key_R[key][0]) + ',' + str(key_R[key][1]) +
                            ',' + str(key_IR[key][0]) + str(key_IR[key][0]) + ',' + str(keyword_probs[key][1]))
            dumpkeyfile.write('\n')
        except:
            dumpkeyfile.write(key + ',' + str(prob) + ',' + str(key_R[key][0]) + ',' + str(key_R[key][1])
                            + ',' + str(1) + ',' + str(0)
                            + ',' + str(keyword_probs[key][1]))
            dumpkeyfile.write('\n')

    objdict_R = get_object_dictionary(decile_one, dump_path='objdict_R_fixed.pkl')
    objdict_reverse = get_object_dictionary(reverse, dump_path='objdict_rev_fixed.pkl') # [FIX: SHOULD INCLUDE DEC 2-10]DONE
    objdict2_10 = get_object_dictionary(deciles2_10, dump_path='objdict2_10_fixed.pkl')
    objdict_IR = {}
    for obj in objdict_reverse:
        if obj in objdict2_10:
            objdict_IR[obj] = [objdict_reverse[obj][0] + objdict2_10[obj][0], objdict_reverse[obj][1] + objdict2_10[obj][1]]
        else:
            objdict_IR[obj] = objdict_reverse[obj]
    pickle.dump(objdict_IR, open('objdict_IR_fixed.pkl', 'w'))

    objects_with_P = get_objects_with_P(objdict_R, objdict_IR, L, dump_path='objects_with_P_fixed.pkl')
    lbt_objects = log_binomial_tail_objs(objects_with_P, objdict_R, Lr, dump_path='lbt_objects_fixed.pkl')
    lbt_sorted = sorted([(x, y[0]) for x,y in lbt_objects.items()], key=operator.itemgetter(1))

    for x in lbt_sorted:
        try:
            dumpobjfile.write(x[0] + '|' + str(x[1]) + '|' + str(objdict_R[x[0]][0]) + '|'+ str(objdict_R[x[0]][1]) +
                     '|' + str(objdict_IR[x[0]][0]) + '|' + str(objdict_IR[x[0]][1])
                     + '|' + str(lbt_objects[x[0]][1]))
        except KeyError:
            dumpobjfile.write(x[0] + '|' + str(x[1]) + '|' + str(objdict_R[x[0]][0]) + '|'+ str(objdict_R[x[0]][1])
                     + '|' + str(1) + '|' + str(0)
                     + '|' + str(lbt_objects[x[0]][1]))
        dumpobjfile.write('\n')

    dumpkeyfile.close()
    dumpobjfile.close()


def do_iteration_2(objects, keywords):
    lnerfed = pickle.load(open(objects, 'r'))

    probs_ml = {k:v for k,v in lnerfed.items() if v == 0}
    search_string_objs = ' '.join(['\"' + x + '\"' for x in probs_ml.keys()][:50]).encode('utf-8')


    key_probs = pickle.load(open(keywords, 'r'))
    keys_ml = {k:v for k,v in key_probs.items() if v == 0}
    search_string_keys = ' '.join(['\"' + x + '\"' for x in keys_ml.keys()][:50]).encode('utf-8')

    fin_hits = indexer.search('stemmed_text:(целеваядат девян "90-е" "90-х" "90-ым") objects:({0}) keywords:({1})'.format(search_string_objs, search_string_keys))

    to_process = fin_hits[:(len(fin_hits) / 12)]

    return to_process

def do_iteration_2_csv(objects, keywords=''):
    line = []
    with open(objects, 'r') as csvfile:
        objs = csv.reader(csvfile)
        for row in objs:
            line.append('\"'+row[0]+'\"')
    line = ' '.join(line)

    if keywords:
        keywordline = []
        with open(keywords, 'r') as csvfile:
            objs = csv.reader(csvfile)
            for row in objs:
                keywordline.append('\"'+row[0]+'\"')
        keywordline = ' '.join(keywordline)
        print(keywordline)
        nhits = indexer.search('stemmed_text:(целеваядат девян "90-е" "90-х" "90-ым") objects:({0}) keywords:({1})'.format(line, keywordline))
        nreverse = indexer.search('*:* NOT stemmed_text:(целеваядат девян "90-е" "90-х" "90-ым") NOT objects:({0}) NOT keywords:({1})'.format(line, keywordline))
        assert len(nhits) + len(nreverse) == len(all)
        return nhits, nreverse

    nhits = indexer.search('stemmed_text:(целеваядат девян "90-е" "90-х" "90-ым") objects:({0})'.format(line))
    nreverse = indexer.search('*:* NOT stemmed_text:(целеваядат девян "90-е" "90-х" "90-ым") NOT objects:({0})'.format(line))
    assert len(nhits) + len(nreverse) == len(all)
    return nhits, nreverse


def draw_graph(nx_graph, show=True):
    layout = nx.spring_layout(nx_graph)
    nx.draw_networkx_nodes(nx_graph, pos=layout, nodelist=nx_graph.nodes())
    nx.draw_networkx_edges(nx_graph, pos=layout, edgelist=nx_graph.edges())
    nx.draw_networkx_labels(nx_graph, pos=layout)

    if show:
        plt.show()
def filter(w):
    counter = 0
    for i in unicode(w):
        if i.isupper() and counter != 0:
            return True

    return False

def network_shenanigans(hits_obj, n):
    bigram_measures = nltk.collocations.BigramAssocMeasures()
    words = get_words(hits_obj)
    finder = BigramCollocationFinder.from_words(words)
    finder.apply_freq_filter(3)
    finder.apply_word_filter(lambda w: w in stopwords)
    finder.apply_word_filter(lambda w: re.search('[0-9]', w))
    finder.apply_word_filter(lambda w: re.search('[a-zA-Z]', w))
    finder.apply_word_filter(lambda w: w.startswith(u'Ъ'))
    finder.apply_word_filter(lambda w: filter(w))
    scored = finder.score_ngrams(bigram_measures.pmi)
    print('Total bigrams:')
    print(len(scored))
    print(scored[5000])

    print('Total collocations:')
    collocations = [x[0] for x in scored if x[1] > n]
    print(len(collocations))

    graph = make_colloc_network(collocations)

    print('Connected components:')
    print(nx.number_connected_components(graph))

    return json_graph.node_link_data(graph)

