# -*- coding: utf-8 -*-
from mongoengine import Document, StringField, IntField
from core.const import TEXT_MAX, TAG_KEY_PREFIX, TAG_DEFAULT_SCORE, BASIC_CACHE_PREFIX, LIMIT, BASIC_TAG_PREFIX
from core.cache import cache
from django.template.defaultfilters import slugify
from unidecode import unidecode
from utils.util import to_unicode
from core.instant_search import SearchIndex
import logging

logger = logging.getLogger('default')

class Tag(Document):
    '''
        Baike data saved in tags tags
        tag name saved in names results
        '''


    slug = StringField(max_length=TEXT_MAX, required=True, unique=True)
    name_en = StringField(max_length=TEXT_MAX, required=True)
    name_zh = StringField(max_length=TEXT_MAX, required=True)
    author_slug = StringField(max_length=TEXT_MAX, default='admin')
    score = IntField(default=TAG_DEFAULT_SCORE)
    description = StringField(max_length=TEXT_MAX, default='')

    @classmethod
    def create_tag(cls, name_zh, *args, **kwargs):
        name_zh = to_unicode(name_zh)
        name_en = unidecode(name_zh)
        slug = slugify(name_en)
        tag = cls(slug=slug, name_en=name_en, name_zh=name_zh, *args, **kwargs)
        try:
            tag.save()
        except Exception as err:
            logging.info("Save Tag Err name_zh %s: err %s" %(name_zh, err))
            return None
        tag.to_info()
        si = SearchIndex()
        si.add_tag(tag)
        return tag

    @property
    def cache_key(self):
        return TAG_KEY_PREFIX + self.slug

    @classmethod
    def get_cache_key(cls, slug):
        return TAG_KEY_PREFIX + slug

    def to_info(self):
        mapping = {
            'slug': self.slug,
            'name_en': self.name_en,
            'name_zh': self.name_zh,
            'author_slug': self.author_slug,
            'description': self.description
        }
        cache.hmset(self.cache_key, mapping)

    @classmethod
    def all_to_info(cls):
        tags = cls.objects()
        for tag in tags:
            tag.to_info()

    @classmethod
    def all_to_search_index(cls):
        tags = cls.objects()
        si = SearchIndex()
        for tag in tags:
            si.add_tag(tag)

    @classmethod
    def see_top_tags(cls):
        keys = cache.keys(pattern='%s*' %BASIC_CACHE_PREFIX)
        set_name = 'TEMP:SET'
        for key in keys:
            value = float(cache.get(key))
            key = key[9:]
            cache.zadd(set_name, value, key)

        results = cache.zrevrange(name=set_name, start=0, num=LIMIT, withscores=True)
        results = [{'name': r[0].decode('utf-8'), 'value': r[1]} for r in results]
        from pymongo import Connection
        c = Connection()
        db = c.names
        if results:
            db.results.insert(results)
        cache.delete(set_name)
        return results

    @classmethod
    def clear_top_tags(cls):
        from pymongo import Connection
        c = Connection()
        db = c.names
        db.results.remove()


    @classmethod
    def loads_basic_tags_to_cache(cls):
        from pymongo import Connection
        c = Connection()
        db = c.names

        tags = db.results.find()
        keys = cache.keys(pattern='%s*' %BASIC_TAG_PREFIX)
        for key in keys:
            cache.delete(key)

        for tag in tags:
            name = tag['name'].split(':')[1]
            key = BASIC_TAG_PREFIX + name
            value = tag['value']
            if int(value) > 1:
                cache.set(key, name)