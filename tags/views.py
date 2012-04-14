# -*- coding: utf-8 -*-
from django.http import Http404, HttpResponse
from tags.models import Tag
from core.instant_search import SearchIndex
import simplejson as json

__author__ = 'chenchiyuan'


def create_tag(request):
    name_zh = request.REQUEST.get('name_zh', '')
    description = request.REQUEST.get('desc', '')
    if not name_zh:
        raise Http404()

    Tag.create_tag(name_zh=name_zh, description=description)
    return HttpResponse("Success")

def search(request):
    term = request.REQUEST.get('term')
    if not term:
        raise Http404()

    si = SearchIndex()
    result = si.search(term)
    return HttpResponse(json.dumps(result))


