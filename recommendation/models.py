# -*- coding: utf-8 -*-
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import StringField, ListField, FloatField, EmbeddedDocumentField
from core.const import TEXT_MAX, SLUG_MAX, SIMILARILY

__author__ = 'chenchiyuan'

from mongoengine import Document, EmbeddedDocument

class PreferEmbedded(EmbeddedDocument):
    slug = StringField(max_length=SLUG_MAX, required=True)
    obj_id = StringField(max_length=TEXT_MAX, required=True)
    name = StringField(max_length=SLUG_MAX, required=True)
    to_id = StringField(max_length=SLUG_MAX, required=True)
    score = FloatField(default=0.0)

class PreferBase(Document):
    obj_id = StringField(max_length=TEXT_MAX, required=True)
    name = StringField(max_length=SLUG_MAX, required=True)
    to_id = StringField(max_length=SLUG_MAX, required=True)
    score = FloatField(default=0.0)

    @classmethod
    def create(cls, obj_id, name, to_id, score=0.0, *args, **kwargs):
        prefer = cls(obj_id=obj_id, name=name, to_id=to_id, score=score, *args, **kwargs)
        try:
            prefer.save()
            return prefer
        except:
            return None

    def get_embedded(self):
        return PreferEmbedded(slug=str(self.id), obj_id=self.obj_id, name=self.name, to_id=self.to_id,
            score=self.score)


class ItemBase(Document):
    #field one to one with Item
    obj_id = StringField(max_length=TEXT_MAX, required=True)
    #name is a valid field, only easy to see
    name = StringField(max_length=SLUG_MAX, required=True)
    #who or what likes the item
    prefers = ListField(EmbeddedDocumentField(PreferEmbedded), default=lambda: [])
    #the old calculate of same items
    sames = ListField(StringField(max_length=TEXT_MAX, default=''), default=lambda: [])
    #tags this item contains
    tags = ListField(StringField(max_length=TEXT_MAX, default=''), default=lambda: [])

    meta = {
        'indexes': ['obj_id']
    }

    def distance(self, item):
        import similarily
        func = getattr(similarily, SIMILARILY)
        return func(self, item)

    @classmethod
    def create(cls, obj_id, name, *args, **kwargs):
        item = cls(obj_id=obj_id, name=name, *args, **kwargs)
        try:
            item.save()
            return item
        except:
            return None
