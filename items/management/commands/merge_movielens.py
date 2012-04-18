# -*- coding: utf-8 -*-
__author__ = 'chenchiyuan'
from django.core.management.base import BaseCommand
from items.models import Base as MovieBase
from recommendation.models import PreferBase, ItemBase

def get_info_from_line(line):
    infos = line.split('::')
    return infos[0], infos[1], infos[2]

def get_rate_from_line(line):
    infos = line.split('::')
    return infos[0], infos[1], infos[2], infos[3]

class Command(BaseCommand):
    def handle(self, *args, **options):
        if not args:
            return

        path = '/home/chenchiyuan/projects/data_set/ml-10M100K/'
        if args[0] == 'movie':
            file = open(path + 'movies.dat')
            lines = file.readlines()
            for line in lines:
                movie_id, name, desc = get_info_from_line(line)
                item = MovieBase.create(name=name, slug=movie_id, description=desc)
                if item:
                    ItemBase.create(obj_id=item.slug, name=item.name)
                    print("save movie name: %s" %item.name)
            file.close()

        elif args[0] == 'rate':
            now = 0
            file = open(path + 'ratings.dat')
            lines = file.readlines()
            for line in lines:
                now += 1
                user_id, movie_id, rate, times = get_rate_from_line(line)
                pre = PreferBase.create(obj_id=user_id, name=user_id, to_id=movie_id, score=float(rate))
                print("%d save pre obj_id %s to to_id %s score %f" %(now, pre.obj_id, pre.to_id, pre.score))
                ItemBase.objects(obj_id=movie_id).update(push__prefers=pre.get_embedded())
            print("total count %d" %now)
            file.close()
