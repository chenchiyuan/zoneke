# -*- coding: utf-8 -*-
__author__ = 'chenchiyuan'
import logging
logger = logging.getLogger('default')
import simplejson as json
from core.const import TIME_PATTERN

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

def datetime_to_str(datetime, fmt=TIME_PATTERN):
    return datetime.strftime(fmt)