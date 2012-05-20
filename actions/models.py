# -*- coding: utf-8 -*-
__author__ = 'chenchiyuan'
from mmseg import seg_txt
from core.cache import cache
from utils.util import unicode_to_str
from core.const import BASIC_TAG_PREFIX
from tags.models import BasicTag

class UserAction(object):
    '''
        User Actions
    '''
    def __init__(self, user):
        self.user = user

    def trace(self):
        pass

    def create_action(self):
        cache_key = "WEIBO:HOT:%s" %self.user.sns_id
        cache.delete(cache_key)

        tmp_cache_key = "TEMP:WEIBO:HISTORY:%s:::" %self.user.sns_id

        weibo_history = self.user.weibo_history

        for text in weibo_history:
            terms = seg_txt(text.encode('utf-8'))
            for term in terms:
                index_key = '%s%s' %(BASIC_TAG_PREFIX, term)
                if cache.exists(index_key):
                    key = tmp_cache_key + term.decode('utf-8')
                    cache.incr(name=key, amount=1)

        keys = cache.keys(pattern="%s*" %tmp_cache_key)

        for key in keys:
            name = key.split(":::")[1]
            value = float(cache.get(key))
            cache.zadd(cache_key, value, name)
            cache.delete(key)

            tag = BasicTag.get_by_name(name=name)
            if not tag:
                continue

            relations = tag.friends
            score = tag.score

            for f in relations:
                items = f.split(':::')
                obj_name = items[0]
                obj_value = float(items[1])
                result = obj_value/50*value
                cache.zadd(cache_key, result, obj_name)

        results = cache.zrevrange(name=cache_key, start=0, num=30, withscores=True)
        tags = [result[0].decode('utf-8') +'__' + str(result[1]) for result in results]

        self.user.update(set__tags=tags)
