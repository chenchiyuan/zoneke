# -*- coding: utf-8 -*-
__author__ = 'chenchiyuan'
from api.weibo import APIClient
from core.const import APP_KEY, APP_SECRET, CALLBACK_URL
from profiles.models import Profile
from utils.util import to_json

from django.http import HttpResponseRedirect, HttpResponse, Http404

def weibo_login(request):
    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
    url = client.get_authorize_url()
    return HttpResponseRedirect(url)

def weibo_callback(request):
    code = request.GET.get('code')
    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
    r = client.request_access_token(code=code)
    access_token = r.access_token
    expires_in = r.expires_in
    client.set_access_token(access_token, expires_in)

    user_data = client.get.users__show(uid=r.uid, access_token=access_token)

    username = user_data['name']
    user_id = user_data['id']
    description = user_data['description']
    avatar_large = user_data['avatar_large']

    user = Profile.create_or_get_user(username=username, password='', access_token=access_token, centroid=[10, 10],
        sns_id=user_id, description=description, avatar=avatar_large, expires_in=expires_in)

    return HttpResponse(to_json(username=user.username, user_id=user.sns_id,
        description=user.description, avatar_large=user.avatar))
     #   mimetype='application/json')\

def weibo_logout(request):
    username = request.GET.get('username', '')
    if not username:
        return HttpResponse(to_json(ret=401))

    user = Profile.get_by_username(username)

    if not user:
        return HttpResponse(to_json(ret=500))

    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
    access_token = user.access_token
    expires_in = user.expires_in
    client.set_access_token(access_token, expires_in)

    client.get.account__end_session()
    user.logout()

    return HttpResponse(to_json(ret=200))