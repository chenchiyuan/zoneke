# -*- coding: utf-8 -*-
from mongoengine import Document, StringField, IntField, EmbeddedDocument, EmbeddedDocumentField
from mongoengine.fields import ListField, FloatField
from core.const import (TEXT_MAX, TAG_KEY_PREFIX, TAG_DEFAULT_SCORE, DAMP, DEFAULT_LIMIT,
                        BASIC_CACHE_PREFIX, LIMIT, BASIC_TAG_PREFIX, DEFAULT_SEG)
from core.cache import cache
from django.template.defaultfilters import slugify
from unidecode import unidecode
from utils.util import to_unicode
from core.instant_search import SearchIndex
import logging

logger = logging.getLogger('default')

from pymongo import Connection
c = Connection()
db = c.tags

class BasicTag(Document):
    '''
        zadd to redis, and get the top 30 tags, else default 0.5
    '''
    name = StringField(max_length=TEXT_MAX, required=True, unique=True)
    score = FloatField(default=0.0)

    #friend is 'name_score' likes 'dota_0.8'
    friends = ListField(default = lambda:[])

    @classmethod
    def create_tag(cls, name, score=0.0, friends=[]):
        tag = cls(name=name, score=score, friends=friends)
        try:
            print("save tag name %s, score %f" %(name, score))
            tag.save()
        except Exception as err:
            pass

    def push_friend(self, tag):
        item = tag.name + DEFAULT_SEG + tag.score
        try:
            self.update(add_to_set__friends=item)
        except Exception as err:
            print(err)

    @classmethod
    def calculate_relations(cls):
        items = cls.objects(friends__size=0)
        for item in items:
            try:
                name = item.name
                tag = db.tags.find_one({'name': name})
            except:
                continue

            if not tag:
                continue

            item_tags = tag['tags']

            for item_tag in item_tags:
                try:
                    cls.__calculate_relation(obj_tag=item_tag, item_name=name)
                except:
                    continue

                keys = cache.keys('TEMP:FRIENDS:%s*' %item_tag)
                for key in keys:
                    name = key.split(':::')[1]
                    cache.zadd('TEMP:%s' %item_tag, float(cache.get(key)), name)
                    cache.delete(key)

                results = cache.zrevrange(name='TEMP:%s' %item_tag, start=0, num=DEFAULT_LIMIT, withscores=True)
                cache.delete('TEMP:%s' %item_tag)

                for r in results:
                    name = r[0].decode('utf-8')
                    score = r[1]/1000
                    if name == item_tag:
                        continue

                    try:
                        obj = cls.objects.get(name=item_tag)
                        obj.update(add_to_set__friends='%s:::%f' %(name, score))
                        print("push %s:::%f to tag %s" %(name, score, item_tag))
                    except :
                        cls.create_tag(name=item_tag, friends=['%s:::%f' %(name, score),])
                        print("push %s:::%f to create tag %s" %(name, score, item_tag))


    @classmethod
    def __calculate_relation(cls, obj_tag, item_name, num=3):
        calculate = cls.objects(name=obj_tag)
        if calculate:
            if calculate[0].friends:
                return

        if num == 0:
            return

        item = db.tags.find_one({'name': item_name})
        if not item:
            return

        item_tags = item['tags']
        damp = round(float(DAMP ** (4 - num)), 3)*1000

        for item_tag in item_tags:
            cache.incr('TEMP:FRIENDS:%s:::%s' %(obj_tag, item_tag), amount=int(damp))

        friends = item['items']
        for friend in friends:
            cls.__calculate_relation(obj_tag, friend, num=num-1)

    @classmethod
    def loads_from_pymongo(cls):
        tem_key = 'TEMP:KEY:'
        items = db.tags.find()
        for item in items:
            for tag in item['tags']:
                print("incr tag name %s" %tag)
                key = tem_key + tag
                cache.incr(name=key, amount=1)

        keys = cache.keys(pattern='%s*' %tem_key)
        for key in keys:
            name = key[9:].decode('utf-8')
            score = float(cache.get(key))
            cls.create_tag(name=name, score=score)
            cache.delete(key)

    meta = {
         'indexes': ['name']
        }

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
