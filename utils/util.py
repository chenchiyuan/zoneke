# -*- coding: utf-8 -*-
__author__ = 'chenchiyuan'
import logging
logger = logging.getLogger('default')
import simplejson as json

def to_unicode(word):
    if isinstance(word, (unicode, type(None))):
        return word
    try:
        return unicode(word, 'utf-8')
    except:
        logger.debug("cannot unicode word %s" %word)
        return None


def to_json(data={}, **kwargs):
    data.update(kwargs)
    return json.dumps(data)