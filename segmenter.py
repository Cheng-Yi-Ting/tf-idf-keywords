#!/usr/bin/python
# -*- coding: utf-8 -*-

import jieba
import re
import codecs
import re
import jieba
import json
import os

with codecs.open('./data/stopword.txt', 'r', encoding='utf-8') as file:
    stopwords = file.read()


def segment(sentence, cut_all=False):
    sentence = sentence.replace("\n", "")
    sentence = sentence.replace("\r", "")
    sentence = sentence.replace("\u3000", "")
    sentence = sentence.strip()
    word = []
    for w in jieba.lcut(sentence,cut_all=cut_all):
        if len(w) > 1 and w not in stopwords and w.isalpha():
            word.append(w)
    # sentence = ' '.join(jieba.cut(sentence, cut_all=cut_all))
    # return re.sub('[a-zA-Z0-9.。:：,，)）(（！!??”“\"]', '', sentence).split()
    return word