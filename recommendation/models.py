# -*- coding: utf-8 -*-
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import StringField, ListField, FloatField
from core.const import TEXT_MAX, SLUG_MAX, SIMILARILY

__author__ = 'chenchiyuan'

from mongoengine import Document

class LikeBase(EmbeddedDocument):
    item_id = StringField(max_length=TEXT_MAX, required=True)
    name = StringField(max_length=SLUG_MAX, required=True)
    score = FloatField(default=0.0)

class ItemBase(Document):
    #field one to one with Item
    obj_id = StringField(max_length=TEXT_MAX, required=True)
    #name is a valid field, only easy to see
    name = StringField(max_length=SLUG_MAX, required=True)
    #who or what likes the item
    likes = ListField(EmbeddedDocument(LikeBase), default=lambda: [])
    #the old calculate of same items
    sames = ListField(StringField=TEXT_MAX, default=lambda: [])
    #tags this item contains
    tags = ListField(StringField=SLUG_MAX, default=lambda: [])

    def distance(self, item):
        import similarily
        func = getattr(similarily, SIMILARILY)
        return func(self, item)