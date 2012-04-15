# -*- coding: utf-8 -*-
__author__ = 'chenchiyuan'
from redis import StrictRedis
from django.conf import settings

def delete_all_keys():
    keys = cache.keys('*')
    for key in keys:
        cache.delete(key)

class RedisCache(StrictRedis):
    pass

cache = RedisCache(host=settings.DB_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


class CacheCenter(object):
    pass
