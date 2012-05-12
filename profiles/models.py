# -*- coding: utf-8 -*-
from mongoengine.django.auth import User
from mongoengine.fields import StringField, GeoPointField, FloatField, ListField
from core.const import SLUG_MAX, TEXT_MAX, PLACE_MSG_CENTER_PREFIX, FEEDS_PREFIX, DEFAULT_PASSWORD
from places.models import Area
from core.instant_search import SearchIndex
from questions.models import Question
from core.cache import cache
import time

__author__ = 'chenchiyuan'


class Profile(User):
    '''
        Profile login from WEIBO

        '''

    #static field
    username = StringField(max_length=SLUG_MAX, required=True, unique=True)
    password = StringField(max_length=TEXT_MAX)
    area_slug = StringField(max_length=SLUG_MAX, default='0 ')
    sns_id = StringField(max_length=TEXT_MAX, default='')
    #logout clear it
    access_token = StringField(max_length=TEXT_MAX, default='')
    expires_in = FloatField(default=0.0)

    #dynamic field
    avatar = StringField(max_length=TEXT_MAX, default='')
    centroid = GeoPointField()
    score = FloatField(default=0.0)
    tags = ListField(StringField(max_length=SLUG_MAX), default=lambda: [])
    history = ListField(StringField(max_length=SLUG_MAX), default=lambda: [])
    description = StringField(max_length=TEXT_MAX, default='')

    meta = {
        'indexes': ['username']
    }

    @property
    def expires(self):
        expires_in = self.expires_in
        if not expires_in:
            return float(300)
        else:
            return float(expires_in)

    def set_expires_in(self, expires_in):
        expires_in += time.time()
        self.update(set__expires_in=expires_in)

    def logout(self):
        #self.update(set__expires_in=0.0)
        pass

    @classmethod
    def create_or_get_user(cls, username, password, access_token, centroid, sns_id, expires_in, *args, **kwargs):
        user = cls(username=username, centroid=centroid, access_token=access_token,
            sns_id=str(sns_id), *args, **kwargs)

        try:
            user = cls.objects.get(username=username)
            user.set_expires_in(expires_in)
            return user
        except:
            pass

        expires_in += time.time()

        area_slug = user.__get_area()
        if not area_slug:
            #TODO something if no area is
            area_slug = '0'
        user.area_slug = area_slug

        if password:
            user.set_password(password)
        else:
            user.set_password(DEFAULT_PASSWORD)

        try:
            user.save()
        except Exception as err:
            print(err)
            return None

        return user

    @classmethod
    def get_by_username(cls, username):
        try:
            user = cls.objects.get(username=username)
        except Exception as err:
            print(err)
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
        self.update_tags(tags=tags)
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
        tags = self.tags
        feeds = []
        for tag in tags:
            channel = self.area_slug + ':' + tag
            feeds.append(cache.rpop(channel))
        return feeds

    def update_tags(self, tags):
        #TODO need some arithmetic
        print("update user tags with tags: %s" %tags)
        tags = self.tags
        if tags:
            tags = [like for like in tags]
            tags = list(set(tags.extend(tags)))
        else:
            tags = tags
        self.update(set__tags=tags)
