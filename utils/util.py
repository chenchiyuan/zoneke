# -*- coding: utf-8 -*-
__author__ = 'chenchiyuan'
import logging
logger = logging.getLogger('default')

def to_unicode(word):
    if isinstance(word, (unicode, type(None))):
        return word
    try:
        return unicode(word, 'utf-8')
    except:
        logger.debug("cannot unicode word %s" %word)
        return None