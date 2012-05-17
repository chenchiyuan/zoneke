# -*- coding: utf-8 -*-
from mongoengine.django.auth import User
from mongoengine.document import Document
from mongoengine.fields import StringField, GeoPointField, FloatField, ListField, DateTimeField
from core.const import (SLUG_MAX, TEXT_MAX, PLACE_MSG_CENTER_PREFIX, FEEDS_PREFIX, DEFAULT_PASSWORD,
                        PROFILE_PREFIX, TALK_PREFIX, SESSION_PREFIX, EXPIRE_WEEK)
from utils.util import datetime_to_str
from places.models import Area
from core.instant_search import SearchIndex
from questions.models import Question
from core.cache import cache, CacheCenter
import time
import datetime

__author__ = 'chenchiyuan'


class Profile(User, CacheCenter):
    '''
        Profile login from WEIBO

        '''

    #static field
    sns_id = StringField(max_length=TEXT_MAX, unique=True)
    username = StringField(max_length=SLUG_MAX, required=True, unique=True)
    password = StringField(max_length=TEXT_MAX)
    area_slug = StringField(max_length=SLUG_MAX, default='0')
    #logout clear it
    access_token = StringField(max_length=TEXT_MAX, default='')
    expires_in = FloatField(default=0.0)

    #dynamic field
    avatar = StringField(max_length=TEXT_MAX, default='')
    centroid = GeoPointField()
    score = FloatField(default=0.0)
    tags = ListField(StringField(max_length=SLUG_MAX), default=lambda: [])
    history = ListField(StringField(max_length=SLUG_MAX), default=lambda: [])
    answers = ListField(StringField(max_length=SLUG_MAX), default=lambda: [])
    likes = ListField(StringField(max_length=SLUG_MAX), default=lambda: [])
    unlikes = ListField(StringField(max_length=SLUG_MAX, default=lambda: []))
    followers = ListField(StringField(max_length=SLUG_MAX, default=lambda: []))
    followings = ListField(StringField(max_length=SLUG_MAX, default=lambda: []))
    description = StringField(max_length=TEXT_MAX, default='')
    weibo_history = ListField(default=[])

    meta = {
        'indexes': ['sns_id', 'username']
    }

    @classmethod
    def cls_cache_key(cls, sns_id):
        return PROFILE_PREFIX + sns_id

    @classmethod
    def to_info_by_obj(cls, obj):
        profile = cls.get_by_sns_id(obj)
        if profile:
            profile.to_info()

    def cache_key(self):
        return PROFILE_PREFIX + self.sns_id

    def mapping(self):
        mapping = {
            'sns_id': self.sns_id,
            'username': self.username,
            'description': self.description,
            'area_slug': self.area_slug,
            'access_token': self.access_token,
            'avatar': self.avatar,
            'score': self.score,
            'tags': self.tags,
            'history': self.history,
            'answers': self.answers,
            'likes': self.likes,
            'unlikes': self.unlikes,
            'followers': self.followers,
            'followings': self.followings,
            'lat': self.centroid[1] if self.centroid else 0,
            'lng': self.centroid[0] if self.centroid else 0,
            }
        return mapping

    @property
    def expires(self):
        expires_in = self.expires_in
        if not expires_in:
            return float(300)
        else:
            return float(expires_in)

    def set_expires_in(self, expires_in):
        self.update(set__expires_in=expires_in)

    def logout(self):
        #self.update(set__expires_in=0.0)
        pass

    def follow(self, user_id):
        user = Profile.get_by_sns_id(user_id)
        if not user:
            return

        try:
            user.update(add_to_set__followers=self.sns_id)
        except Exception as err:
            print(err)

        try:
            self.update(add_to_set__followings=user_id)
        except Exception as err:
            print(err)

    def unfollow(self, user_id):
        if not user_id in self.followings:
            return

        user = Profile.get_by_sns_id(user_id)
        if not user:
            return

        try:
            user.update(pull__followers=self.sns_id)
        except Exception as err:
            print(err)

        try:
            self.update(pull__followings=user_id)
        except Exception as err:
            print(err)

    def like(self, item_id):
        try:
            self.update(add_to_set__likes=item_id)
        except Exception as err:
            print(err)

    def unlike(self, item_id):
        try:
            self.update(add_to_set__unlikes=item_id)
        except Exception as err:
            print(err)

    def answer(self, question_id):
        pass

    @classmethod
    def create_or_get_user(cls, username, password, access_token, centroid, sns_id, expires_in, *args, **kwargs):
        user = cls(username=username, centroid=centroid, access_token=access_token,
            sns_id=str(sns_id), *args, **kwargs)

        try:
            user = cls.objects.get(username=username)
            user.set_expires_in(expires_in)
            user.update(set__access_token=access_token)
            user.reload()
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

    @classmethod
    def get_by_sns_id(cls, sns_id):
        try:
            user = cls.objects.get(sns_id=sns_id)
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

    def talk_to(self, user_sns_id, content=''):
        if isinstance(user_sns_id, Profile):
            user_sns_id = user_sns_id.sns_id

        session = Session.create_session(user_sns_id=user_sns_id, content=content)

        talk = Talk.get_or_create_by_users(user_a=self.sns_id, user_b=user_sns_id)
        if session:
            talk.add_session(session)

    def get_talk_history_with_user(self, user):
        pass


class Talk(Document, CacheCenter):
    #owner is two people who's sns_id smaller
    owner = StringField(max_length=TEXT_MAX)
    talk_to = StringField(max_length=TEXT_MAX, unique_with='owner')

    history = ListField(StringField(max_length=TEXT_MAX), default=[])

    meta = {
        'indexes': [('owner', 'talk_to'),]
    }

    @classmethod
    def cls_cache_key(cls, obj):
        return TALK_PREFIX + str(obj)

    @classmethod
    def to_info_by_obj(cls, obj):
        try:
            talk = Talk.objects.get(id=obj)
        except Exception as err:
            print(err)
            return

        talk.to_info()

    def cache_key(self):
        return TALK_PREFIX + str(self.id)

    def mapping(self):
        user_a_info = Profile.get_info_by_obj(self.owner)
        user_b_info = Profile.get_info_by_obj(self.talk_to)
        user_info = {
            self.owner: user_a_info,
            self.talk_to: user_b_info
        }

        history = []
        for session_id in self.history:
            info = Session.get_info_by_obj(session_id)
            print(info)
            sns_id = info['sns_id']
            info['username'] = user_info[sns_id]['username']
            info['avatar'] = user_info[sns_id]['avatar']
            info['lat'] = user_info[sns_id]['lat']
            info['lng'] = user_info[sns_id]['lng']
            history.append(info)

        mapping = {
            'owner': self.owner,
            'talk_to': self.talk_to,
            'history': history
        }

        return mapping

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

class Session(Document, CacheCenter):
    user_sns_id = StringField(max_length=SLUG_MAX, required=True)
    content = StringField(max_length=TEXT_MAX, default='')
    updated_at = DateTimeField(default=datetime.datetime.now())

    @classmethod
    def cls_cache_key(cls, id):
        return SESSION_PREFIX + str(id)

    @classmethod
    def to_info_by_obj(cls, obj):
        session = Session.get_by_id(obj)
        if session:
            session.to_info()

    def cache_key(self):
        return SESSION_PREFIX + str(self.id)

    def mapping(self):
        mapping = {
            'sns_id': self.user_sns_id,
            'content': self.content,
            'updated_at': datetime_to_str(self.updated_at)
        }
        return mapping

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