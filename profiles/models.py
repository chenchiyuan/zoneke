# -*- coding: utf-8 -*-
from mongoengine.django.auth import User
from mongoengine.fields import StringField, GeoPointField, FloatField, ListField
from core.const import SLUG_MAX, TEXT_MAX, PLACE_MSG_CENTER_PREFIX, FEEDS_PREFIX
from places.models import Area
from core.instant_search import SearchIndex
from questions.models import Question
from core.cache import cache

__author__ = 'chenchiyuan'


class Profile(User):
    '''
        Profile login from WEIBO

        '''

    #static field
    username = StringField(max_length=SLUG_MAX, required=True, unique=True)
    password = StringField(max_length=TEXT_MAX, required=True)
    area_slug = StringField(max_length=SLUG_MAX, required=True)
    snsid = StringField(max_length=TEXT_MAX, default='')

    #dynamic field
    centroid = GeoPointField()
    score = FloatField(default=0.0)
    likes = ListField(StringField(max_length=SLUG_MAX), default=lambda: [])
    history = ListField(StringField(max_length=SLUG_MAX), default=lambda: [])

    @classmethod
    def create_user(cls, username, password, centroid, *args, **kwargs):
        user = cls(username=username, centroid=centroid, *args, **kwargs)
        area_slug = user.__get_area()
        if not area_slug:
            #TODO something if no area is
            area_slug = '0'
        user.area_slug = area_slug

        if password is not None:
            user.set_password(password)

        try:
            user.save()
        except:
            return None

        return user

    def __get_area(self):
        #TODO use within_distance is a best way, the follow is just test
        areas = Area.objects(centroid__near=self.centroid)
        if areas.count():
            return areas[0].slug
        else:
            return None

    def ask(self, title, content, lat, lng):
        centroid = (lng, lat)

        search = SearchIndex()
        tags = search.parse(title)
        self.update_likes(tags=tags)
        question = Question.create(title=title, area_slug=self.area_slug, centroid=centroid,
            author_name=self.username, content=content, tags=tags)
        self.publish(question)

    def publish(self, question):
        tags = question.tags
        area_slug = question.area_slug
        for tag in tags:
            channel = FEEDS_PREFIX + area_slug + ':' + tag
            cache.publish(channel=channel, message=str(question.id))

    def get_feeds(self):
        self.reload()
        tags = self.likes
        feeds = []
        for tag in tags:
            channel = self.area_slug + ':' + tag
            feeds.append(cache.rpop(channel))
        return feeds

    def update_likes(self, tags):
        #TODO need some arithmetic
        print("update user likes with tags: %s" %tags)
        likes = self.likes
        if likes:
            likes = [like for like in likes]
            likes = list(set(likes.extend(tags)))
        else:
            likes = tags
        self.update(set__likes=likes)
