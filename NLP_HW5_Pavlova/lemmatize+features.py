import re
import pymorphy2
import csv


RE_LEMMA = re.compile('^([а-яё]+?)_')
RE_MEANING = re.compile('\t([0-9])\n?')
RE_POS = re.compile('^....')
RE_NUM = re.compile('(plur)|(sing)')
KEYWORDS = [('модельный', 'один', 'первый', 'второй', 'третий', 'четвертый', 'пятый', 'последний', 'предпоследний',
             'верхний', 'задний', 'звуковой', 'ассоциативный', 'визуальный', 'вон', 'выходящий', 'синонимический',
             'задний', 'длинный', 'стоять', 'стоявший', 'лежать', 'лежавший', 'сидеть', 'сидевший', 'двигаться',
             'шагать', 'выстроиться', 'сесть', 'лечь', 'встать', 'между', 'театр', 'сцена'),
            ('целый', 'случай', 'страна', 'государство', 'параметр', 'мера', 'вопрос', 'ограничение', 'задача',
             'преимущество', 'решение', 'причина', 'требование'),
            ('вступление', 'вступить', 'трутень', 'поклонник', 'пополнить', 'пополнение', 'товарищ', 'член',
             'партийный'),
            ('калашный', 'охотный', 'торговый'),
            ('натуральный', 'число', 'математический')]


# через нижнее подчеркивание _часть речи и _число
def lemmatize(path):
    sentences = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            sentence = []
            m = RE_MEANING.search(line)
            if m:
                meaning = m.group(1)
                line = RE_MEANING.sub('', line)
            else:
                print('no meaning detected')
            words = line.split(' ')
            words = [word.strip('.,/-–―"?!()[]<>…:;') for word in words]
            words = [word for word in words if len(word) > 0]
            for word in words:
                analysis = morph.parse(word)[0]
                lemma = analysis.normal_form
                p = RE_POS.search(str(analysis.tag))
                if p:
                    pos = p.group()
                else:
                    print('no pos detected')
                n = RE_NUM.search(str(analysis.tag))
                if n:
                    number = n.group()
                else:
                    number = 'none'
                sentence.append('{}_{}_{}'.format(lemma, pos, number))
            sentence.append(meaning)
            sentences.append(sentence)
    return sentences


def print_sent(sentences, path):
    with open(path, 'w', encoding='utf-8') as f:
        for sentence in sentences:
            f.write('{}\n'.format(' '.join(sentence)))


def get_features(sentences, path):
    header = ('prevword', 'nextword', 'prevpos', 'nextpos', 'prevnum', 'nextnum', 'number', 'class')
    rows = []
    for sentence in sentences:
        prevword, nextword, prevpos, nextpos, prevnum, nextnum = None, None, None, None, None, None
        c = sentence[-1]
        for w in range(len(sentence) - 1):
            if sentence[w].startswith('ряд_'):
                lemma, pos, number = sentence[w].split('_')
                try:
                    prevword, prevpos, prevnum = sentence[w - 1].split('_')
                except ValueError:
                    pass
                try:
                    nextword, nextpos, nextnum = sentence[w + 1].split('_')
                except ValueError:
                    pass

        rows.append((prevword, nextword, prevpos, nextpos, prevnum, nextnum, number, c))
    with open(path, 'w', encoding='utf-8') as w:
        out = csv.writer(w, delimiter=',')
        out.writerow(header)
        out.writerows(rows)


def get_keyword_features(sentences, path):
    header = ('prevword', 'nextword', 'prevpos', 'nextpos', 'prevnum', 'nextnum', 'number', 'class',
              'class_1', 'class_3', 'class_4', 'class_5', 'class_8')
    rows = []
    for sentence in sentences:
        prevword, nextword, prevpos, nextpos, prevnum, nextnum = None, None, None, None, None, None
        c = sentence[-1]
        classes = [0, 0, 0, 0, 0]
        for w in range(len(sentence) - 1):
            l = RE_LEMMA.search(sentence[w])
            if l:
                for i in range(len(KEYWORDS)):
                    if l.group(1) in KEYWORDS[i]:
                        classes[i] = 1
            if sentence[w].startswith('ряд_'):
                lemma, pos, number = sentence[w].split('_')
                try:
                    prevword, prevpos, prevnum = sentence[w - 1].split('_')
                except ValueError:
                    pass
                try:
                    nextword, nextpos, nextnum = sentence[w + 1].split('_')
                except ValueError:
                    pass

        rows.append((prevword, nextword, prevpos, nextpos, prevnum, nextnum, number, c,
                     str(classes[0]), str(classes[1]), str(classes[2]), str(classes[3]), str(classes[4])))
    with open(path, 'w', encoding='utf-8') as w:
        out = csv.writer(w, delimiter=',')
        out.writerow(header)
        out.writerows(rows)


if __name__ == '__main__':
    morph = pymorphy2.MorphAnalyzer()
    sentences = lemmatize('rjad_200.csv')
    print_sent(sentences, 'lemmatized_rjad.txt')
    get_features(sentences, 'rjad_features.csv')
    get_keyword_features(sentences, 'rjad_keyword_features.csv')
