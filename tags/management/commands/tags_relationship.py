# -*- coding: utf-8 -*-
__author__ = 'chenchiyuan'

from django.core.management.base import BaseCommand
from core.cache import cache
import os

LIMIT_FRIENDS = 10
BASIC_TAGS = [u'编程语言', u'游戏', u'音乐', u'电影', u'书籍']

damping = 1
BASIC_KEY = 'TAG:RELATION:::'
TMP_KEY = 'TEMP:TOP:TAG:'

class Command(BaseCommand):
    def handle(self, *args, **options):
        path = os.getcwd() + '/data/'
#        files = os.listdir(path)
#
#        for file_name in files:
#            file = open(path + file_name, 'r')
#            lines = file.readlines()
#            for line in lines:
#                try:
#                    load = False
#                    line.replace('::::::', ':::')
#                    line.replace(':::::', ':::')
#                    line.replace('::::', ':::')
#                    tags_str = line.split(':::')[3]
#                    tags = tags_str.split('__')
#                    for tag in tags:
#                        if cache.exists(name='%s%s' %(TMP_KEY, tag)):
#                            load = True
#                            break
#
#                    if load:
#                        tag = tags[0]
#                        for last in tags[1:]:
#                            key1 = '%s%s' %(BASIC_KEY, tag)
#                            key2 = '%s%s' %(BASIC_KEY, last)
#                            cache.zincrby(name=key1, value=last, amount=damping)
#                            cache.zincrby(name=key2, value=tag, amount=damping)
#
#                except Exception as err:
#                    print(err)
#                    continue

        path = path + 'basic_tags/'
        keys = cache.keys('%s*' %BASIC_KEY)

        file = open(path + 'relations', 'w')
        for key in keys:
            print("load %s" %key[15:])
            data = cache.zrevrangebyscore(name=key, max='+inf', min='-inf', withscores=True)
            name = key[15:]
            values = '__'.join([l[0]+':::'+str(l[1]) for l in data])
            file.write(name + '\t' + values + '\n')
        file.close()