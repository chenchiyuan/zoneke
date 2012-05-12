# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from core.const import TYPES, BASIC_CACHE_PREFIX, BASIC_TAG_PREFIX
from pymongo import Connection
from core.cache import cache
from tags.models import Tag

c = Connection()
db = c.tags
type_db = c.names

BASIC_TAGS = [u'编程语言', u'游戏', u'音乐', u'餐厅', u'电影', u'书籍']

__author__ = 'chenchiyuan'

def filter_tags():
    tags = db.tags.find()
    for tag in tags:
        remove = True
        items = tag['tags']
        for item in items:
            key = BASIC_TAG_PREFIX + item
            if cache.exists(key):
                remove = False
                break

        if remove:
            db.tags.remove({'_id': tag['_id']})
        else:
            print("retain tag %s" %tag['name'])


def delete_keys():
    keys = cache.keys(pattern='%s*' %BASIC_CACHE_PREFIX)
    print("keys count %d" %len(keys))
    for key in keys:
        cache.delete(key)

def load_tags():
    db.tags.remove()


def generate_basic_tags():
    Tag.clear_top_tags()

    for basic in BASIC_TAGS:
        delete_keys()
        items = db.tags.find()

        for item in items:
            print("processed item %s" %item['name'])
            if not basic in item['tags']:
                continue

            for tag in item['tags']:
                key = BASIC_CACHE_PREFIX + basic + ':' + tag
                cache.incr(key, amount=1)

        results = Tag.see_top_tags()

    Tag.loads_basic_tags_to_cache()
    delete_keys()

class Command(BaseCommand):
    def handle(self, *args, **options):
        if not args:
            return

        dict = {
            'load': load_tags,
            'filter': filter_tags,
            'generate': generate_basic_tags
        }

        if args[0] not in dict.keys():
            print("arg need filter or generate")
            return

        func = dict[args[0]]
        func()