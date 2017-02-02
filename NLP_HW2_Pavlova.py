'''
Золотой стандарт - триграмы из НКРЯ, где суд в NOM SG
удалены лексические функции, иногда изменен вид глагола,
не входят триграммы, которых нет в спец. корпусе.
'''

import nltk
from nltk.collocations import *
from nltk.metrics.spearman import *


bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measures = nltk.collocations.TrigramAssocMeasures()


def find_gold(gold, metric):
    ranked_metric = list(ranks_from_scores(metric))
    metric_gold = []
    for trigram1 in gold:
        metric_gold.append((trigram1, 1000))
        for trigram2 in ranked_metric:
            if trigram1 == trigram2[0]:
                metric_gold[-1] = trigram2
    return metric_gold


def print_corr_matrix(arrays):
    corr_matrix = []
    for array1 in arrays:
        corr_line = []
        for array2 in arrays:
            rho = spearman_correlation(array1, array2)
            corr_line.append('%0.1f' % rho)
        corr_matrix.append(corr_line)
    for line in corr_matrix:
        print(line)


def court_collocations(path):
    lines = open('court-V-N.csv').readlines()

    # делаем массив массивов со словами для каждой строки без суда
    documents = []
    for line in lines:
        words = line.strip('\r\n').split(',')
        words = [word.strip(' ').lower() for word in words]
        documents.append(words)

    # выделяем коллокации из массива массивов
    finder = TrigramCollocationFinder.from_documents(documents)

    # не рассматриваем триграммы с частотой меньше 5
    finder.apply_freq_filter(5)

    # удаляем стопслова и слова короче 3 символов
    stopwords = nltk.corpus.stopwords.words('russian')
    finder.apply_word_filter(lambda w: len(w) < 3 or w.lower() in stopwords)

    # лучшие триграммы по метрике PMI, первое слово - суд
    trigrams_pmi = sorted(finder.score_ngrams(trigram_measures.pmi),
                          reverse=True, key=lambda x: x[1])
    court_tri_pmi = [trigram for trigram in trigrams_pmi
                     if trigram[0][0] == 'суд']
    print('PMI')
    print(court_tri_pmi[:10])

    # лучшие триграммы по метрике LogLikelihood, первое слово - суд
    trigrams_log = sorted(finder.score_ngrams(trigram_measures.likelihood_ratio),
                          reverse=True, key=lambda x: x[1])
    court_tri_log = [trigram for trigram in trigrams_log
                     if trigram[0][0] == 'суд']
    print('\nLogLikelihood')
    print(court_tri_log[:10])

    # самые частотные триграммы, первое слово - суд
    trigrams_freq = sorted(finder.score_ngrams(trigram_measures.raw_freq),
                           reverse=True, key=lambda x: x[1])
    court_tri_freq = [trigram for trigram in trigrams_freq
                      if trigram[0][0] == 'суд']
    print('\nFrequency')
    print(court_tri_freq[:10])

    # считаем ранговую корреляцию с золотым стандартом
    gold = [('суд', 'вынести', 'определение'), ('суд', 'вынести', 'решение'),
            ('суд', 'удовлетворить', 'иск'), ('суд', 'вынести', 'приговор'),
            ('суд', 'рассматривать', 'дело'), ('суд', 'рассмотреть', 'дело'),
            ('суд', 'прекратить', 'производство'), ('суд', 'слушать', 'дело'),
            ('суд', 'решить', 'дело'), ('суд', 'признать', 'виновная')]
    court_pmi_gold = find_gold(gold, court_tri_pmi)
    court_log_gold = find_gold(gold, court_tri_log)
    court_freq_gold = find_gold(gold, court_tri_freq)

    print('\nBig ranks')
    # ranks PMI
    print(court_pmi_gold)
    # ranks LogLikelihood
    print(court_log_gold)
    # ranks frequency
    print(court_freq_gold)
    # ranks gold
    gold_ranks = list(ranks_from_sequence(gold))
    print(gold_ranks)

    arrays = [gold_ranks, court_freq_gold, court_pmi_gold, court_log_gold]

    print('\nCorrelation matrix')
    print_corr_matrix(arrays)

    print('\nRanks 0-9')
    court_pmi_gold_little = list(ranks_from_sequence(
        [trigram[0] for trigram in sorted(court_pmi_gold, key=lambda x: x[1])]))
    court_log_gold_little = list(ranks_from_sequence(
        [trigram[0] for trigram in sorted(court_log_gold, key=lambda x: x[1])]))
    court_freq_gold_little = list(ranks_from_sequence(
        [trigram[0] for trigram in sorted(court_freq_gold, key=lambda x: x[1])]))
    print(court_pmi_gold_little)
    print(court_log_gold_little)
    print(court_freq_gold_little)
    print(gold_ranks)

    print('\nCorrelation matrix')
    arrays = [court_pmi_gold_little, court_log_gold_little, court_freq_gold_little, gold_ranks]
    print_corr_matrix(arrays)


if __name__ == '__main__':
    court_collocations('court-V-N.csv')
    print('вывод: использовались pmi, loglikelihood, для прикола частота.\n'
          'все довольно плохо коррелируют с золотым стандартом, что не удивительно,\n'
          'потому что он составлялся по частоте в корпусе + некоторые исправления\n'
          'для списка по частоте корреляция 0.6 при фильтре частоты = 5.')