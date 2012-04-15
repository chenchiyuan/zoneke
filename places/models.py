# -*- coding: utf-8 -*-
from mongoengine.document import Document
from mongoengine.fields import StringField, GeoPointField, ListField
from core.const import CENTER_PLACE, PER_GEO, SLUG_MAX, PLACE_MSG_CENTER_PREFIX
from place_listener import PlaceMsgCenter

__author__ = 'chenchiyuan'

class Area(Document):
    '''
        Area is a special model.
        example, wuhan is a area. and when created it , the slug field is created according to lat & lng.
        everyone in this area, can register to the area, can push & pull feeds from the area.
        every area run a new thread in background, listen to the redis, maintain the cache hash table of this area
        in debug: just create it before. think how to do it dynamic next
                                 0 0.1(2),

                -0.1, 0(3)  0, 0(0)      0.1, 0(1)

                                -0.1, 0(4)
        '''

    #NOTICE centroid is lng, lat. save carefully
    slug = StringField(required=True, unique=True)
    centroid = GeoPointField(required=True)
    user_list = ListField(StringField(max_length=SLUG_MAX), default=lambda: [])
    channels = ListField(StringField(max_length=SLUG_MAX), default=lambda: [])

    @classmethod
    def generate_area(cls, max_num=5):
        center = CENTER_PLACE
        def get_lat_lng(slug):
            num, mod = divmod(slug, 4)
            if mod == 1:
                return  num*PER_GEO + center[0], center[1]
            elif mod == 2:
                return center[0], center[1] + num*PER_GEO
            elif mod == 3:
                return center[0] - num*PER_GEO, center[1]
            else:
                return center[0], center[1] - num*PER_GEO

        for slug in range(max_num):
            lat, lng = get_lat_lng(slug)
            centroid = [lng, lat]
            cls.__create(slug=str(slug), centroid=centroid)

    @property
    def cache_key(self):
        return PLACE_MSG_CENTER_PREFIX + self.slug

    @classmethod
    def __create(cls, slug, centroid, *args, **kwargs):
        area = cls(slug=slug, centroid=centroid, *args, **kwargs)
        area.save()
        center = PlaceMsgCenter(slug=area.slug)
        center.start()

    @property
    def centorid(self):
        return centorid[1], centorid[0]