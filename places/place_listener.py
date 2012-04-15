# -*- coding: utf-8 -*-
__author__ = 'chenchiyuan'
from core.cache import cache
from threading import Thread
from core.const import PLACE_MSG_CENTER_PREFIX

class PlaceMsgCenter(Thread):
    '''
    new a thread to listen to messages
    when new a PlaceMsgCenter:
        1. init it in cache
        2. listen all the feeds channels
        3. user only get infos from PlaceMsgCenter Cache
    '''

    def __init__(self, slug):
        Thread.__init__(self, name=slug)
        self.slug = slug
        self.pubsub = cache.pubsub()
        self.cache_key = PLACE_MSG_CENTER_PREFIX + slug

    def to_cache(self):
        mapping = {
            'slug': self.slug,
            'user_list': [],
            'channels': [],
        }
        cache.hmset(self.cache_key, mapping)

    def run(self):
        self.pubsub.psubscribe('feed:%s:*' %self.slug)
        for msg in self.pubsub.listen():
            channel = msg['channel']
            data = msg['data']
            tag_name = channel[5:]
            cache.lpush(tag_name, data)

