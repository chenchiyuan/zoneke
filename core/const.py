# -*- coding: utf-8 -*-
__author__ = 'chenchiyuan'

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

#default
TAG_DEFAULT_SCORE = 0