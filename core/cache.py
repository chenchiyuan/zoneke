# -*- coding: utf-8 -*-
__author__ = 'chenchiyuan'
import redis
from django.conf import settings

cache = redis.StrictRedis(host=settings.DB_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

def delete_all_keys():
    keys = cache.keys('*')
    for key in keys:
        cache.delete(key)