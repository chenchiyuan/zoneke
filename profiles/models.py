# -*- coding: utf-8 -*-
from mongoengine.django.auth import User
from mongoengine.document import Document
from mongoengine.fields import StringField, GeoPointField, FloatField, ListField, DateTimeField
from core.const import SLUG_MAX, TEXT_MAX, PLACE_MSG_CENTER_PREFIX, FEEDS_PREFIX, DEFAULT_PASSWORD
from places.models import Area
from core.instant_search import SearchIndex
from questions.models import Question
from core.cache import cache
import time
import datetime

__author__ = 'chenchiyuan'


class Profile(User):
    '''
        Profile login from WEIBO

        '''

    #static field
    sns_id = StringField(max_length=TEXT_MAX, unique=True)
    username = StringField(max_length=SLUG_MAX, required=True, unique=True)
    password = StringField(max_length=TEXT_MAX)
    area_slug = StringField(max_length=SLUG_MAX, default='0 ')
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
        'indexes': ['sns_id', 'username']
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

    def talk_to(self, user, content=''):
        session = Session.create_session(user_sns_id=user.sns_id, content=content)

        talk = Talk.get_or_create_by_users(user_a=self.sns_id, user_b=user.sns_id)
        if session:
            talk.add_session(session)

    def get_talk_history_with_user(self, user):
        pass


class Talk(Document):
    #owner is two people who's sns_id smaller
    owner = StringField(max_length=TEXT_MAX)
    talk_to = StringField(max_length=TEXT_MAX, unique_with='owner')

    history = ListField(StringField(max_length=TEXT_MAX), default=[])

    meta = {
        'indexes': [('owner', 'talk_to'),]
    }

    def add_session(self, session):
        try:
            self.update(push__history=str(session.id))
        except Exception as err:
            print(err)

    @classmethod
    def create_talk(cls, user_a, user_b):
        owner, talk_to = cls.__get_owner_talk_to(user_a, user_b)

        talk = Talk(owner=owner, talk_to=talk_to)
        try:
            talk.save()
        except Exception as err:
            print(err)
            return None

        return talk

    @classmethod
    def get_or_create_by_users(cls, user_a, user_b):
        owner, talk_to = cls.__get_owner_talk_to(user_a, user_b)

        try:
            return cls.objects.get(owner=owner, talk_to=talk_to)
        except Exception as err:
            print(err)
            return cls.create_talk(user_a, user_b)

    @classmethod
    def __get_owner_talk_to(cls, user_a, user_b):
        tmp_user_a = float(user_a)
        tmp_user_b = float(user_b)

        owner = user_a if tmp_user_a < tmp_user_b else user_b
        talk_to = user_a if tmp_user_a > tmp_user_b else user_b
        return owner, talk_to



class Session(Document):
    user_sns_id = StringField(max_length=SLUG_MAX, required=True)
    content = StringField(max_length=TEXT_MAX, default='')
    updated_at = DateTimeField(default=datetime.datetime.now())

    def to_info(self):
        pass

    @classmethod
    def create_session(cls, user_sns_id, content, **kwargs):
        session = Session(user_sns_id=user_sns_id, content=content)
        try:
            session.save()
        except Exception as err:
            print(err)
            return None

        return session

    @classmethod
    def get_by_id(cls, id):
        try:
            return cls.objects.get(id=id)
        except Exception as err:
            print(err)
            return None