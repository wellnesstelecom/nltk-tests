#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#

"""
import twits to redis
"""

from urllib import urlopen
import json
import redis

POSITIVE_URL = "http://search.twitter.com/search.json?q=%3A%29&lang=es"
NEGATIVE_URL = "http://search.twitter.com/search.json?q=%3A%28&lang=es"

def get(url):
    return urlopen(url).read()

def parse_twits(atom_text):
    return [(x['id'],x['text']) for x in json.loads(atom_text)['results']]


def insert(cat, url):
    r = redis.Redis()
    a = 0
    for id, text in parse_twits(get(url)):
        a += r.hset(cat, str(id), text)
    return a

import time
while True:
    print "%d positive inserted" % insert('cat:positive', POSITIVE_URL)
    print "%d negative inserted" % insert('cat:negative', NEGATIVE_URL)
    time.sleep(1)





