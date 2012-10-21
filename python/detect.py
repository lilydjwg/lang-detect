#!/usr/bin/env python
# -*- coding: utf-8 -*-#

"""
Detect the language for a small piece of unicode text.
Usage:
    langdetect YOUR_SENTENCE
"""

import os
import re
import codecs
import math
import json
import sys
import getopt

class Alphabet():
    def __init__(self, json):
        self.data = json
        self.keys = sorted(list(json.keys()), key=lambda name: json[name]['interval'][0])
    def which(self, c):
        lo=0
        hi=None
        if hi is None:
            hi = len(self.keys)
        while lo < hi:
            mid = (lo+hi)//2
            midval_lower = self.data[self.keys[mid]]['interval'][0]
            midval_upper = self.data[self.keys[mid]]['interval'][1]
            if int(midval_upper, 16) < ord(c):
                lo = mid+1
            elif int(midval_lower, 16) > ord(c):
                hi = mid
            else:
                return self.data[self.keys[mid]]
        return None
    def n(self, c):
        seg = self.which(c)
        if seg is None:
            return 1
        else:
            return seg['n']

class GramGenerator():
    def __init__(self, alphabet, text):
        self.alphabet = alphabet
        self.text = text
        self.iterator = next_gram(self)
    def __iter__(self):
        return self.iterator()

position = -1
def next_gram(gg):
    global position
    length   = len(gg.text)
    position = -1
    def gram():
        global position
        while True:
            position = position + 1
            if position >= length:
                position = -1
                raise StopIteration
            c = gg.text[position]
            n = gg.alphabet.n(c)
            if n < 1: n = 1
            end = position + n
            if end >= length - 1:
                position = -1
                raise StopIteration
            else:
                yield gg.text[position:end]
    return gram

f = codecs.open(os.path.join(os.path.dirname(__file__), 'meta', 'alphabet.json'), 'r', 'utf-8')
alphabet = Alphabet(json.loads(str(''.join(f.readlines()))))

langs = ['en', 'ja', 'zh-hans', 'zh-hant']

vectors = {}
for lang in langs:
    vectors[lang] = {}
    f = codecs.open(os.path.join(os.path.dirname(__file__), 'data', lang + '.txt'), 'r', 'utf-8')
    for line in f:
        segs = line.split(', 0.')
        if len(segs) == 2:
            key = segs[0]
            val = float('0.' + segs[1])
            vectors[lang][key] = val

def inner(a, b):
    comm = set(a.keys()) & set(b.keys())
    val = 0.0
    for key in comm:
        val = val + a[key] * b[key]
    return val

def detect(text):
    freq = {}
    gg = GramGenerator(alphabet, text)
    for gram in gg:
        if gram in list(freq.keys()):
            freq[gram] = freq[gram] + 1
        else:
            freq[gram] = 1

    sq = 0
    for k in list(freq.keys()):
        sq = sq + freq[k] * freq[k]
    l = math.sqrt(sq)

    for k in list(freq.keys()):
        freq[k] = float(freq[k]) / l

    sim = {}
    for lang in langs:
        sim[lang] = inner(vectors[lang], freq)

    keys = sorted(list(sim.keys()), key=lambda ind: -sim[ind])
    return [(key, sim[key]) for key in keys]

def main():
    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.error as msg:
        print(msg)
        print("for help use --help")
        sys.exit(2)
    # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
    for l in sys.stdin:
        print('===================================')
        print(l)
        guessings = detect(l)
        for result in guessings:
            lang, sim = result
            print(lang + ':' + str(sim))

if __name__ == "__main__":
    main()

