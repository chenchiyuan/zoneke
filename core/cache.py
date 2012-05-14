# -*- coding: utf-8 -*-
__author__ = 'chenchiyuan'
from redis import StrictRedis
from django.conf import settings
from core.const import EXPIRE_WEEK

def delete_all_keys():
    keys = cache.keys('*')
    for key in keys:
        cache.delete(key)

class RedisCache(StrictRedis):
    pass

cache = RedisCache(host=settings.DB_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


class CacheCenter(object):
    def cache_key(self):
        return 'DEFAULT'

    def mapping(self):
        return {}

    def to_info(self, time=EXPIRE_WEEK):
        key = self.cache_key()
        mapping = self.mapping()
        cache.hmset(name=key, mapping=mapping)
        cache.expire(name=key, time=time)

    def get_info(self):
        key = self.cache_key()
        mapping = cache.hgetall(name=key)
        if not mapping:
            self.to_info()
            mapping = cache.hgetall(name=key)

        return mapping

    def clear_cache(self, pattern=''):
        if not pattern:
            pattern = '%s*' %(self.cache_key())

        keys = cache.keys(pattern=pattern)
        for key in keys:
            cache.delete(key)

    @classmethod
    def cls_cache_key(cls, obj):
        return obj

    @classmethod
    def get_info_by_obj(cls, obj):
        key = cls.cls_cache_key(obj)
        mapping = cache.hgetall(name=key)

        if not mapping:
            cls.to_info_by_obj(obj)
            mapping = cache.hgetall(name=key)

        return mapping

    @classmethod
    def to_info_by_obj(cls, obj):
        pass

    @classmethod
    def clear_all_cache(cls, pattern=''):
        if not pattern:
            pattern = '%s*' %(cls.cls_cache_key(''))

        keys = cache.keys(pattern=pattern)
        for key in keys:
            cache.delete(key)


