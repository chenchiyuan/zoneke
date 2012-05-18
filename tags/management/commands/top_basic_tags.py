# -*- coding: utf-8 -*-

__author__ = 'chenchiyuan'

from django.core.management.base import BaseCommand
from core.cache import cache
import os

LIMIT_FRIENDS = 10
BASIC_TAGS = [u'编程语言', u'游戏', u'音乐', u'电影', u'书籍']

def load_tag(tag):
    key = 'TEMP:TOP:TAG:' + tag
    cache.incr(name=key, amount=1)

class Command(BaseCommand):
    def handle(self, *args, **options):
        path = os.getcwd() + '/data/'
        files = os.listdir(path)

        for file_name in files:
            file = open(path + file_name, 'r')
            lines = file.readlines()
            for line in lines:
                try:
                    load = False
                    line.replace('::::::', ':::')
                    line.replace(':::::', ':::')
                    line.replace('::::', ':::')
                    tags_str = line.split(':::')[3]
                    tags = tags_str.split('__')
                    for tag in tags:
                        if tag.decode('utf-8') in BASIC_TAGS:
                            load = True
                            break

                    if load:
                        for tag in tags:
                            load_tag(tag)

                except Exception as err:
                    print(err)
                    continue

#        keys = cache.keys(pattern='TEMP:TOP:TAG:*')
#        Z_KEY = 'TOP:TAG'
#        for key in keys:
#            try:
#                value = cache.get(name=key)
#                cache.zadd(Z_KEY, float(value), key[13:])
#            except Exception as err:
#                print(err)
#                continue

