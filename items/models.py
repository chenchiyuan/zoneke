# -*- coding:utf-8 -*-
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField, FloatField
from core.const import TEXT_MAX, SLUG_MAX

__author__ = 'chenchiyuan'

class Base(Document):
    slug = StringField(max_length=SLUG_MAX, default='')
    name = StringField(max_length=SLUG_MAX, required=True)
    tags = ListField(default=lambda: [])
    description = StringField(max_length=TEXT_MAX, default='')
    score = FloatField(default=0.0)

    @classmethod
    def create(cls, name, *args, **kwargs):
        base = cls(name=name, *args, **kwargs)
        try:
            base.save()
            return base
        except:
            return None

    meta = {
        'allow_inheritance': True,
        'indexes': ['slug']
    }

class Music(Base):
    pass

class Movie(Base):
    pass


