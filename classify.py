#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# author: javi santana

"""
classify twitts (stored in redis) and try to guess mood
"""

import redis
import nltk
import random

REMOVE_WORDS = """&quot &amp http esta""".split()

def text_from_raw(text):
    """
        >>> txt = text_from_raw("mi perro es verde")
        >>> len(txt)
        4
    """
    text = nltk.clean_html(text)
    tokens = nltk.word_tokenize(text)
    return nltk.Text(tokens)

def word_freq(text, maxwords=2000):
    """
        >>> w = word_freq(text_from_raw('hola que tal, hola'))
        >>> w[0]
        'hola'
    """
    all_words = nltk.FreqDist(w.lower() for w in text.tokens)
    return [x for x in all_words.keys() if len(x) >=4 and x not in REMOVE_WORDS][:maxwords]

def twits(cat):
    r = redis.Redis()
    tw = r.hgetall(cat)
    return tw.values()

def proccess_twits(cat):
    tw = twits(cat)
    text = text_from_raw('\n'.join((x for x in tw if len(x) >= 8 and ':P' not in x)))
    return word_freq(text, 200)

def document_features(document, word_set):
    document_words = set(document)
    features = {}
    for word in word_set:
        features['contains(%s)' % word] = (word in document_words)
    return features

if __name__ == '__main__':
    word_set = proccess_twits('cat:positive') + proccess_twits('cat:negative')
    positive = [(text_from_raw(t), 'positive') for t in twits('cat:positive')]
    negative = [(text_from_raw(t), 'negative') for t in twits('cat:negative') if ':P' not in t and ':p' not in t]
    all = positive + negative
    print len(all)
    random.shuffle(all)

    featuresets = [(document_features(d, word_set), c) for (d,c) in all]
    train_set, test_set = featuresets[1::2], featuresets[::2]
    classifier = nltk.NaiveBayesClassifier.train(train_set)
    print nltk.classify.accuracy(classifier, test_set)


