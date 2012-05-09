# -*- coding: utf-8 -*-
__author__ = 'chenchiyuan'

TYPES = {
    '0': u'编程语言',
    '1': u'游戏',
    '2': u'音乐',
    '3': u'餐厅',
    '4': u'餐馆',
    '5': u'电影',
    '6': u'书籍'
}

#TAGS
LIMIT = 70

#RECOMMENDATION SETTINGS
SIMILARILY = 'euclid' # euclid, pearson

#place settings
CENTER_PLACE = (10, 10)
PER_GEO = 1

#mongoengine
TEXT_MAX = 256
SLUG_MAX = 64

#index
SEARCH_KEY_PREFIX = "CACHE:SEARCH:"
TAG_KEY_PREFIX = "CACHE:TAG:"
PLACE_MSG_CENTER_PREFIX = "PLACE:MSG:"
FEEDS_PREFIX = "FEEDS:"
BASIC_CACHE_PREFIX = 'TEMP:TAG:'
BASIC_TAG_PREFIX = 'BASIC:TAG:'

#default
TAG_DEFAULT_SCORE = 0