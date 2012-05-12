# -*- coding: utf-8 -*-
__author__ = 'chenchiyuan'

from core.const import DOUBAN_API_KEYS
import random
import urllib2, urllib

import simplejson as json
import datetime
import re

BASE_URL = 'http://api.douban.com/'
OBJ_TYPE = ['book', 'movie', 'music']

class DoubanParse:
    def parseEntry(self, entrys):
        if not entrys:
            return []

        m = re.compile('http://api.douban.com/\w+/subject/(.+)')
        result = []
        for entry in entrys:
            subjectID = ''
            for link in entry['link']:
                if link['@rel'] == 'self':
                    g = m.match(link['@href'])
                    subjectID = g.group(1)
            result.append(subjectID)
        return result

    def search_movie(self, json_data):
        result = {
            'nums': json_data.get('opensearch:totalResults', 0),
            'title': json_data.get('title', ''),
            'entrys': self.parseEntry(json_data.get('entry', '')),
            'start': json_data.get('opensearch:startIndex', 0),
            'per_page': json_data.get('opensearch:itemsPerPage', 0),
            }
        return result

    def search_book(self, json_data):
        result = {
            'nums': json_data.get('opensearch:totalResults', 0),
            'title': json_data.get('title', ''),
            'entrys': self.parseEntry(json_data.get('entry', '')),
            'start': json_data.get('opensearch:startIndex', 0),
            'per_page': json_data.get('opensearch:itemsPerPage', 0),
            }
        return result

    def search_music(self, json_data):
        result = {
            'nums': json_data.get('opensearch:totalResults', 0),
            'title': json_data.get('title', ''),
            'entrys': self.parseEntry(json_data.get('entry', '')),
            'start': json_data.get('opensearch:startIndex', 0),
            'per_page': json_data.get('opensearch:itemsPerPage', 0),
            }
        return result

    def parse_movie(self, obj_id, json_data):
        data = {
            'author': json_data.get('author', []),
            'title': json_data.get('title', {}),
            'summary': json_data.get('summary', 'blank'),
            'link': json_data['link'],
            'attr': json_data['db:attribute'],
            'id_url': json_data['id'],
            'rating': json_data['gd:rating'],
            'type': 'movie',
            'category': json_data.get('category', 'blank')
        }
        result = {'subjectID': obj_id,
                  'tags':json_data['db:tag'],
                  'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                  }
        result.update(data)
        return result

    def parse_music(self, obj_id, json_data):
        data = {
            'author': json_data.get('author', []),
            'title': json_data.get('title', {}),
            'summary': json_data.get('summary', 'blank'),
            'link': json_data['link'],
            'attr': json_data['db:attribute'],
            'id_url': json_data['id'],
            'rating': json_data['gd:rating'],
            'type': 'music',
            'category': json_data.get('category', 'blank')
        }
        result = {'subjectID': obj_id,
                  'tags':json_data['db:tag'],
                  'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                  }
        result.update(data)
        return result

    def parse_book(self, obj_id, json_data):
        data = {
            'author': json_data.get('author', []),
            'title': json_data.get('title', {}),
            'summary': json_data.get('summary', 'blank'),
            'link': json_data['link'],
            'attr': json_data['db:attribute'],
            'id_url': json_data['id'],
            'rating': json_data['gd:rating'],
            'type': 'book',
            }
        result = {'subjectID': obj_id,
                  'tags':json_data['db:tag'],
                  'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                  }
        result.update(data)
        return result

class Douban:
    def __init__(self):
        self.api_key = random.choice(DOUBAN_API_KEYS)

    def search(self, obj_type='book', q=None, tag=None, start= 0, max=100):
        if not (q or tag):
            return None

        attr = {
            'start-index': str(start),
            'max-results': str(max),
            'alt': 'json',
            'apikey': self.api_key
        }

        if q:
            attr['q'] = q
        if tag:
            attr['tag'] = tag


        search_types = OBJ_TYPE
        if obj_type:
            search_types = [obj_type, ]

        parse = DoubanParse()

        result = {}
        for item in search_types:
            data_hander = getattr(self, '_search_%s' %item)
            json_data = data_hander(attr)

            parse_hander = getattr(parse, 'search_%s' %item)
            result[item] = parse_hander(json_data)

        return result

    def get(self, obj_id, obj_type='book'):
        if not obj_type in OBJ_TYPE:
            return None

        parse = DoubanParse()

        get_handle = getattr(self, '_get_%s' %obj_type)
        json_data = get_handle(obj_id)

        parse_handle = getattr(parse, 'parse_%s' %obj_type)
        result = parse_handle(obj_id, json_data)

        return result

    def _get_book(self, obj_id):
        url = '%s%s/subject/%s?alt=json&apikey=%s' %(BASE_URL, 'book', obj_id, self.api_key)
        request = urllib2.Request(url)

        try:
            response = urllib2.urlopen(request)
        except Exception as err:
            print(err)
            return None

        return self._read_data_from_response(response)

    def _get_movie(self, obj_id):
        url = '%s%s/subject/%s?alt=json&apikey=%s' %(BASE_URL, 'movie', obj_id, self.api_key)
        request = urllib2.Request(url)

        try:
            response = urllib2.urlopen(request)
        except Exception as err:
            print(err)
            return None

        return self._read_data_from_response(response)

    def _get_music(self, obj_id):
        url = '%s%s/subject/%s?alt=json&apikey=%s' %(BASE_URL, 'book', obj_id, self.api_key)
        request = urllib2.Request(url)

        try:
            response = urllib2.urlopen(request)
        except Exception as err:
            print(err)
            return None

        return self._read_data_from_response(response)

    def _read_data_from_response(self, response):
        data = ''
        while True:
            temp = response.read(1024)
            if not len(temp):
                break

            data += temp

        ls = data.split('$')
        data = '@'.join(ls)
        return json.loads(data)

    def _search_music(self, attr):
        url = '%s%s/subjects?' %(BASE_URL, 'music') + urllib.urlencode(attr)
        request = urllib2.Request(url)

        try:
            response = urllib2.urlopen(request)
        except Exception as err:
            print(err)
            return None

        return self._read_data_from_response(response)


    def _search_book(self, attr):
        url = '%s%s/subjects?' %(BASE_URL, 'book') + urllib.urlencode(attr)
        request = urllib2.Request(url)

        try:
            response = urllib2.urlopen(request)
        except Exception as err:
            print(err)
            return None

        return self._read_data_from_response(response)

    def _search_movie(self, attr):
        url = '%s%s/subjects?' %(BASE_URL, 'movie') + urllib.urlencode(attr)
        request = urllib2.Request(url)

        try:
            response = urllib2.urlopen(request)
        except Exception as err:
            print(err)
            return None

        return self._read_data_from_response(response)