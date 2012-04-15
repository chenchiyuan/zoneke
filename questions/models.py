# -*- coding: utf-8 -*-
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField, DateTimeField, FloatField, GeoPointField
from core.const import SLUG_MAX, TEXT_MAX
from datetime import datetime

__author__ = 'chenchiyuan'

class Question(Document):
    '''
        the base Question model, id uses mongoDB default ID
        '''
    #static field
    title = StringField(max_length=SLUG_MAX, required=True)
    area_slug = StringField(max_length=SLUG_MAX, required=True)
    author_name = StringField(max_length=SLUG_MAX, required=True)
    centroid = GeoPointField(required=True)
    content = StringField(max_length=TEXT_MAX, default='')
    tags = ListField(StringField(max_length=SLUG_MAX), default=lambda: [])
    created_at = DateTimeField(default=lambda: datetime.now())
    effect_at = DateTimeField(default=lambda: None)

    #dynamic field
    score = FloatField(default=0.0)

    @classmethod
    def create(cls, title, area_slug, author_name, centroid, *args, **kwargs):
        question = cls(title=title, area_slug=area_slug, author_name=author_name,
            centroid=centroid, *args, **kwargs)
        try:
            question.save()
            return question
        except:
            return None



